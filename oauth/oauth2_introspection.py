import json
import logging
import requests

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework.permissions import BasePermission

from oauth2_provider.models import get_access_token_model

log = logging.getLogger(__name__)

UserModel = get_user_model()
AccessToken = get_access_token_model()


class HasClaim(BasePermission):
    """
    Use claim (from the userinfo response) to determine permission.
    N.B. this only works for an external OAuth2/OIDC AS that returns claims in the userinfo response.
    """
    #: the `claim identifier <https://openid.net/specs/openid-connect-core-1_0.html#Claims>`_
    claim = None
    #: map by HTTP method of which word in the claim must be present.
    #: claim values are assumed to be a list of words (similar to scopes).
    claims_map = {
        'GET': None,
        'OPTIONS': None,
        'HEAD': None,
        'POST': None,
        'PUT': None,
        'PATCH': None,
        'DELETE': None,
    }

    def __init__(self):
        """
        See if our OAuth2/OIDC AS even has the userinfo endpoint
        """
        if 'userinfo_endpoint' in settings.OAUTH2_CONFIG:
            self.userinfo_url = settings.OAUTH2_CONFIG['userinfo_endpoint']
        else:
            self.userinfo_url = None
        log.debug('userinfo_url: {}'.format(self.userinfo_url))

    def _get_claims_from_authentication_server(self, token):
        """
        get the userinfo response for the given access token
        :param token: Bearer Access Token from request's Authorization header
        :return: :string: serialized userinfo response or None
        """
        if self.userinfo_url is None:  # userinfo is not implemented
            return None

        try:
            access_token = AccessToken.objects.select_related("application", "user").get(token=token)
        except Exception as e:
            log.error(e)
            return None

        if access_token.userinfo:  # already stashed it.
            return access_token.userinfo

        try:
            response = requests.get(self.userinfo_url, headers={'authorization': 'Bearer {}'.format(token)})
        except requests.exceptions.RequestException:
            log.exception("Userinfo: Failed GET to %r in token lookup", self.userinfo_url)
            return None

        if response.status_code == 200:
            access_token.userinfo = response.content.decode('utf-8')
            access_token.save()
        return access_token.userinfo

    def has_permission(self, request, view):
        """
        If an OIDC `claim` name was configured along with a `claim_map` that looks for a given claim value
        then return true if the claim value is present in the userinfo response.
        If the mapping is None then return False.
        If the mapping is the empty string then return True.
        """
        if self.claim is None:
            assert False, 'HasClaim called but not configured.'

        if request.method in self.claims_map:
            log.debug('HasClaim: looking for {} in userinfo["{}"] for token "{}"'
                      .format(self.claim, self.claims_map[request.method], request.auth))

        if (request.method in self.claims_map
            and hasattr(request, 'auth')
            and hasattr(request.auth, 'userinfo')):
            if request.auth.userinfo is None:
                request.auth.userinfo = self._get_claims_from_authentication_server(request.auth)
            log.debug('userinfo result >>{}<<'.format(request.auth.userinfo))
            try:
                claims = json.loads(request.auth.userinfo)[self.claim].split()
                if self.claims_map[request.method] is None:
                    return False
                elif self.claims_map[request.method] == '':
                    return True
                elif self.claims_map[request.method] in claims:
                    return True
            except Exception as e:
                log.error(e)
                return False
        else:
            return False
