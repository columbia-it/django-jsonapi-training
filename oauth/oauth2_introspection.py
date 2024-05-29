import json
import logging
from typing.re import Pattern

import requests
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from oauth2_provider.models import get_access_token_model
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin
from rest_framework.permissions import BasePermission

log = logging.getLogger(__name__)

UserModel = get_user_model()
AccessToken = get_access_token_model()


class HasClaim(BasePermission, OAuthLibMixin):
    """
    Use claim (from the userinfo response) to determine permission.
    N.B. this only works for an OIDC AS that returns claims in the userinfo response.
    """

    # TODO: make claim values be a list of strings or RE's.
    #: the `claim identifier <https://openid.net/specs/openid-connect-core-1_0.html#Claims>`_
    claim = None
    #: map by HTTP method of which word in the claim must be present.
    #: claim values are assumed to be a string list of words (similar to scopes) or RE.
    claims_map = {
        "GET": None,
        "OPTIONS": None,
        "HEAD": None,
        "POST": None,
        "PUT": None,
        "PATCH": None,
        "DELETE": None,
    }

    def __init__(self):
        """
        See if our OAuth2/OIDC AS even has the userinfo endpoint
        """
        self.userinfo_url = oauth2_settings.OIDC_USERINFO_ENDPOINT
        log.debug(
            "OIDC enabled: {}, userinfo_url: {}".format(
                oauth2_settings.OIDC_ENABLED, self.userinfo_url
            )
        )

    def _get_claims_from_authentication_server(self, request):
        """
        get the external userinfo response for the given access token
        :param request: request.auth has the access token
        :return: :string: serialized userinfo response or None
        """
        try:
            access_token = AccessToken.objects.select_related(
                "application", "user"
            ).get(token=request.auth)
        except Exception as e:
            log.error(e)
            return None

        if access_token.userinfo:  # already stashed it.
            return access_token.userinfo

        try:
            response = requests.get(
                self.userinfo_url,
                headers={"authorization": "Bearer {}".format(request.auth)},
            )
        except requests.exceptions.RequestException:
            log.exception(
                "Userinfo: Failed GET to %r in token lookup", self.userinfo_url
            )
            return None

        if response.status_code == 200:
            access_token.userinfo = response.content.decode("utf-8")
            access_token.save()
        return access_token.userinfo

    def _get_claims_from_oauthlib(self, request):
        """
        return the userinfo response from oauthlib when using internal AS and OIDC is enabled.
        Args:
            request:

        Returns: userinfo response JSON string
        """
        if not oauth2_settings.OIDC_ENABLED:
            return None
        try:
            access_token = AccessToken.objects.select_related(
                "application", "user"
            ).get(token=request.auth)
        except Exception as e:
            log.error(e)
            return None

        if access_token.userinfo:  # already stashed it.
            return access_token.userinfo

        core = self.get_oauthlib_core()
        _, _, userinfo, status = core.create_userinfo_response(request)
        if status == 200:
            access_token.userinfo = userinfo
            access_token.save()
            return access_token.userinfo
        else:
            log.error("userinfo error {}".format(status))

    def has_permission(self, request, view):
        """
        If an OIDC `claim` name was configured along with a `claim_map` that looks for a given claim value
        then return true if the claim value is present in the userinfo response.
        If the mapping is None then return False.
        If the mapping is the empty string then return True.
        """
        if self.claim is None:
            raise ImproperlyConfigured("HasClaim called but not configured.")

        if request.method in self.claims_map:
            log.debug(
                'HasClaim: looking for {} claim {} value "{}"'.format(
                    request.method, self.claim, self.claims_map[request.method]
                )
            )

        if (
            request.method in self.claims_map
            and hasattr(request, "auth")
            and hasattr(request.auth, "userinfo")
        ):
            if request.auth.userinfo is None:
                if self.userinfo_url:
                    request.auth.userinfo = self._get_claims_from_authentication_server(
                        request
                    )
                else:
                    request.auth.userinfo = self._get_claims_from_oauthlib(request)
            log.debug("userinfo result >>{}<<".format(request.auth.userinfo))
            try:
                claims_map_entry = self.claims_map[request.method]
                if claims_map_entry is None:
                    log.debug(
                        "Claim denied (None means False)"
                    )  # TODO: change up to use True/False?
                    return False
                if claims_map_entry == "":
                    log.debug("Claim approved (empty string means True)")
                    return True
                claim_value = json.loads(request.auth.userinfo)[self.claim]
                if isinstance(claims_map_entry, str):
                    claims = claim_value.split()
                    if claims_map_entry in claims:
                        log.debug(
                            'Claim approved ("{}" is in {})'.format(
                                claims_map_entry, claims
                            )
                        )
                        return True
                    else:
                        log.debug(
                            'Claim denied ("{}" not in {})'.format(
                                claims_map_entry, claims
                            )
                        )
                        return False
                elif isinstance(claims_map_entry, Pattern):
                    if claims_map_entry.match(claim_value):
                        log.debug(
                            'Claim approved ("{}" matches {})'.format(
                                claim_value, claims_map_entry
                            )
                        )
                        return True
                    else:
                        log.debug(
                            'Claim denied ("{}" does not match {})'.format(
                                claim_value, claims_map_entry
                            )
                        )
                        return False
                else:
                    log.error("claim value must be of type str or re")
                    return False
            except Exception as e:
                log.error(e)
                return False
        else:
            return False
