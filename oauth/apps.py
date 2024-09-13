import json
import logging

import requests
from django.apps import AppConfig
from django.conf import settings
from django.urls import reverse
from oauth2_provider.settings import oauth2_settings


class OauthConfig(AppConfig):
    name = "oauth"
    log = logging.getLogger(name)

    def ready(self):
        """
        Connect to settings.OAUTH2_SERVER's well-known openid-configuration to fill out settings.OAUTH2_CONFIG.
        If the server is 'self' then fill it in as if we had connected to the internal server's well-known...
        """
        oidc_server = getattr(settings, "OAUTH2_SERVER", None)
        if oidc_server == "self":
            baseUrl = 'http://127.0.0.1:8000'  # TODO figure this out
            settings.OAUTH2_CONFIG = json.dumps({
                "issuer": baseUrl,
                "authorization_endpoint": baseUrl + reverse("oauth2_provider:authorize"),
                "token_endpoint": baseUrl + reverse("oauth2_provider:token"),
                "userinfo_endpoint": baseUrl + reverse("oauth2_provider:user-info"),
                "jwks_uri": baseUrl + reverse("oauth2_provider:jwks-info"),
                "scopes_supported": [s for s in oauth2_settings.SCOPES],
                "response_types_supported": [
                    "code",
                    "token",
                    "id_token",
                    "id_token token",
                    "code token",
                    "code id_token",
                    "code id_token token"
                ],
                "subject_types_supported": [
                    "public"
                ],
                "id_token_signing_alg_values_supported": [
                    "RS256",
                    "HS256"
                ],
                "token_endpoint_auth_methods_supported": [
                    "client_secret_post",
                    "client_secret_basic"
                ],
                "code_challenge_methods_supported": [
                    "plain",
                    "S256"
                ],
                "claims_supported": [
                    "sub"
                ]
            }, indent=4)

        elif oidc_server is not None:
            url = oidc_server + "/.well-known/openid-configuration"
            print(f"trying {url}")
            try:
                result = requests.get(url, timeout=10)
                if result.status_code == 200:
                    settings.OAUTH2_CONFIG = result.json()
                    settings.OAUTH2_PROVIDER["SCOPES"]: {
                        k: f"{k} scope"  # noqa F722
                        for k in settings.OAUTH2_CONFIG["scopes_supported"]  # noqa F821
                    }
                    self.log.debug(
                        "succesfully initialized OAUTH2_CONFIG for {}".format(
                            settings.OAUTH2_SERVER
                        )
                    )
                else:
                    self.log.error("failed to get {}".format(url))
            except requests.exceptions.RequestException as e:
                self.log.error(e)
        else:
            settings.OAUTH2_CONFIG = None
