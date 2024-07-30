from django.conf import settings
from pprint import pprint
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object

class OAuth2AccessTokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'oauth2_provider.contrib.rest_framework.OAuth2Authentication'
    name = 'OAuth2'

    def get_security_definition(self, auto_schema):
        # TODO -- flesh out Django-oauth-toolkit stuff
        r = build_bearer_security_scheme_object(header_name='AUTHORIZATION',
                                                   token_prefix='Bearer',)
        pprint(r)
        return r
