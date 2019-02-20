import os
import webbrowser
import http.server
import threading
import requests
import pyperclip
import time
import uuid
from pprint import pformat
import logging
from oauthlib.oauth2 import WebApplicationClient, MobileApplicationClient, BackendApplicationClient
from urllib.parse import parse_qs, splitport, urlparse

log = logging.getLogger(__name__)


class MyOAuth2Session(object):
    """
    Establish an OAuth2 "session" using raw oauthlib.

    For authorization_code and implicit flows, this will open a browser to log the user in.
    In order to test token refresh without having to wait, you can set `expire_faster` to a smaller number.
    """
    # TODO: Consider replacing all this with requests-oauthlib

    def __init__(self, oauth_server=None, client_id=None, client_secret=None, redirect_url=None, grant=None,
                 scopes=None, refresh_token=None, expire_faster = None):
        """
        establish an OAuth 2 session (acquire Access Token, etc)
        :param oauth_server: base URL of the oauth2 server
        :param client_id: OAuth 2 client ID
        :param client_secret: OAuth 2 client secret
        :param redirect_url: OAuth 2 client's registers redirect URL
        :param grant: type: 'authorization_code', etc.
        :param scopes: list of requested scopes
        :param refresh_token: OAuth 2 refresh token for 'refresh_token' grant
        :param expire_faster: Seconds until access token expires. Used to override the default expires_in.
        """
        self.oauth_server = oauth_server
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url
        self.grant = grant
        self.scopes = scopes
        self.refresh_token = refresh_token
        self.expire_faster = expire_faster
        #: generate Authorization Basic header with client ID and secret.
        self.oauth_auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        #: oauthlib client is set in one of do_authorization_code, do_implicit, etc.
        self.oauth_client = None
        # get oauth 2.0 endpoints by asking the AS for them:
        r = requests.get(oauth_server + '/.well-known/openid-configuration')
        if r.status_code == 200:
            self.oauth_endpoints = r.json()
        else:
            raise ConnectionError("failed to get OAuth 2 endpoints: {} {}: {}".format(r.status_code, r.reason, r.content))
        # if we are testing with non-TLS then tell oauthlib that's OK
        if not redirect_url.startswith('https'):
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    class BearerAuth(requests.auth.AuthBase):
        """
        Creates a callable that sets "Authorization: Bearer <access_token>" header for requests.
        Usage example::

          response = requests.get(url, body=body, data=data, headers=headers, auth=BearerAuth(access_token))

        """
        def __init__(self, access_token = None):
            if access_token:
                self.access_token = access_token

        def __call__(self, r):
            r.headers['Authorization'] = 'Bearer ' + self.access_token
            return r

    def set_tokens(self):
        """
        parse out the various tokens from the OAuth 2 Token response
        """
        if self.oauth_tokens:
            self.access_token = self.oauth_tokens['access_token'] if 'access_token' in self.oauth_tokens else None
            # possibly replace the current refresh token with a new one due to refresh token rolling policy in the AS.
            self.refresh_token = self.oauth_tokens['refresh_token'] if 'refresh_token' in self.oauth_tokens else None
            self.id_token = self.oauth_tokens['id_token'] if 'id_token' in self.oauth_tokens else None
            self.expires_in = self.oauth_tokens['expires_in'] if 'expires_in' in self.oauth_tokens else None
            if self.expire_faster and self.expires_in and self.expire_faster < self.expires_in:
                self.expires_in = self.expire_faster
            self.expires_at = self.expires_in + time.time() if self.expires_in else None
        else:
            self.access_token = self.refresh_token = self.id_token = self.expires_in = self.expires_at = None

    def do_authorization_code(self):
        """
        login to OAuth 2 using Authorization Code grant
        """
        self.oauth_client = WebApplicationClient(self.client_id)
        (authorize_url, headers, body) = self.oauth_client.prepare_authorization_request(
            self.oauth_endpoints['authorization_endpoint'], redirect_url=self.redirect_url, scope=self.scopes)
        status, code_request_url = self._redirect_server(self.redirect_url, authorize_url)
        if not code_request_url:
            input("Copy URL to clipboard and then hit enter:")
            code_request_url = pyperclip.paste()
        if status != 200 or 'error_description' in code_request_url:
            r = urlparse(code_request_url)
            errors = parse_qs(r.query)
            if 'error' in errors and 'error_description' in errors:
                msg = "{}: {}".format(errors['error'][0], errors['error_description'][0])
                raise TimeoutError(msg) if status == 408 else RuntimeError(msg)
            else:
                msg = pformat(errors)
                raise TimeoutError(msg) if status == 408 else RuntimeError(msg)

        (url, headers, body) = self.oauth_client.prepare_token_request(
            self.oauth_endpoints['token_endpoint'],
            authorization_response=code_request_url,
            redirect_url=self.redirect_url)
        token_response = requests.post(url, headers=headers, data=body, auth=self.oauth_auth)
        if token_response.status_code != 200:
            raise PermissionError(self._format_response_error(token_response))
        self.oauth_tokens = token_response.json()
        self.set_tokens()

    def do_refresh_token(self):
        """
        Use the refresh token to get new tokens.
        Refresh tokens are only used with the Authorization Code grant.

        Can be called either from the get-go with a supplied refresh_token or later on
        to refresh an existing access_token.

        Not that depending on how the OAuth 2.0 AS is configured, the refresh token is rotated after
        each use (or some amount of time). This can mitigate replays of a stolen refresh token but
        will raise an exception if you try to reuse an invalid refresh token::

            PermissionError: 400: invalid_grant: unknown, invalid, or expired refresh token

        """
        if not self.refresh_token:
            raise ValueError("no refresh token supplied for `refresh_token` grant")
        if self.oauth_client is None:
            self.oauth_client = WebApplicationClient(self.client_id)
        (token_url, headers, body) = self.oauth_client.prepare_refresh_token_request(
            self.oauth_endpoints['token_endpoint'],
            refresh_token=self.refresh_token,
            scope=self.scopes)
        token_response = requests.post(token_url, headers=headers, data=body, auth=self.oauth_auth)
        if token_response.status_code != 200:
            raise PermissionError(self._format_response_error(token_response))
        self.oauth_tokens = token_response.json()
        self.set_tokens()

    def do_implicit(self):
        """
        Implicit grant
        """
        self.oauth_client = MobileApplicationClient(self.client_id)
        (token_url, headers, body) = self.oauth_client.prepare_authorization_request(self.oauth_endpoints[
                                                                               'authorization_endpoint'],
            redirect_url=self.redirect_url, scope=self.scopes, )
        # For openid scope, have to add id_token response_type and supply a nonce:
        # https://www.pingidentity.com/content/developer/en/resources/openid-connect-developers-guide/implicit-client
        # -profile.html
        # "Note: To mitigate replay attacks, a nonce value must be included to associate a client session with an
        # id_token. The client must generate a random value associated with the current session and pass this
        # along with the request. This nonce value will be returned with the id_token and must be verified to be
        # the same as the value provided in the initial request."
        #
        # oauthlib `lacks client features<https://github.com/oauthlib/oauthlib/issues/615>`_ for OIDC.
        if 'openid' in self.scopes:
            self.nonce = uuid.uuid4().hex
            # TODO: fix this to something more robust or extend oauthlib
            token_url = token_url.replace('response_type=token',
                                          'response_type=token+id_token&nonce={}'.format(self.nonce))
        # for the implicit grant type, the parameters are provided to the browser as #fragments rather than
        # ?query-parameters so they are never available to the redirect server. The user must copy the
        # browser
        self._redirect_server(self.redirect_url, token_url,
                              message="Copy this URL to the clipboard and hit enter on the console. "
                                      "Then you can close this window.")
        input("\n\nCopy URL to clipboard and then hit enter:")
        token_response_url = pyperclip.paste()
        self.oauth_tokens = self.oauth_client.parse_request_uri_response(token_response_url)
        self.set_tokens()

    def do_client_credentials(self):
        """
        Client credentials grant
        """
        self.oauth_client = BackendApplicationClient(self.client_id)
        (token_url, headers, body) = self.oauth_client.prepare_token_request(self.oauth_endpoints['token_endpoint'],
                                                                             scope=self.scopes)
        token_response = requests.post(token_url, headers=headers, data=body, auth=self.oauth_auth)
        if token_response.status_code != 200:
            raise PermissionError(self._format_response_error(token_response))
        self.oauth_tokens = token_response.json()
        self.set_tokens()

    @staticmethod
    def _format_response_error(response):
        """
        make a pretty error response message::
          status_code: reason error: error_description

        :param response: request.request() response
        :return: string formatted with status_code, reason and json-parsed 'error' and 'error_description' (if json)
        """
        try:
            content = response.json()
            error = content['error'] + ': ' if 'error' in content else ''
            error_msg = error + content['error_description'] if 'error_description' in content else content
        except:
            error_msg = response.reason + ':' + response.content.decode()
        return "{}: {}".format(response.status_code, error_msg)

    def _redirect_server(self, redirect_url, authorize_url, message='Response received. You can close this window.'):
        """
        Run an http server thread to catch the OAuth 2 redirect and then exit.

        :param redirect_url: redirect_url
        :param authorize_url: authorization request
        :param message: success message to display in the browser
        :return: status, redirected request path containing parameters
        """

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                """ silence the default log_message that http.server prints for each request """
                pass

            def do_GET(self):
                """
                implement http GET method.
                """
                # the browser may ask for stupid things like /favicon.ico
                # so check to make sure it's the redirect_uri that we expect
                if self.path.startswith(server.redirect_path_prefix):
                    server.path = self.path
                    server.semaphore.set()
                    response = message.encode()
                else:
                    response = b'huh?'
                self.send_response(200, 'OK')
                self.send_header("Content-type", 'text/plain')
                self.send_header("Content-Length", len(response))
                self.end_headers()
                try:
                    self.wfile.write(response)
                finally:
                    self.wfile.flush()

        r = urlparse(redirect_url)
        if r.port is None:
            port = 443 if redirect_url.startswith("https") else 80
        else:
            port = r.port
        server_address = ('127.0.0.1', port)
        server = http.server.HTTPServer(server_address, Handler)
        server.redirect_path_prefix = r.path
        server.semaphore = threading.Event()
        server.path = None
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        webbrowser.open_new(authorize_url)
        signaled = server.semaphore.wait(timeout=30)
        if not signaled:
            log.debug("redirect server timed out")
            status = 408
            path = '/?error=timeout&error_description=redirect+server+wait+timed+out'
        else:
            status = 200
            path = server.path
        server.shutdown()
        thread.join()
        return status, path
