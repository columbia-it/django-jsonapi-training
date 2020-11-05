from django.conf import settings
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.authentication import BasicAuthentication
from rest_framework_json_api.schemas.openapi import SchemaGenerator as JSONAPISchemaGenerator

from myapp import __author__, __copyright__, __license__, __license_url__, __title__, __version__


class MyOAuth2Auth(OAuth2Authentication):
    """
    Temporary workaround until DRF 3.13 merges https://github.com/encode/django-rest-framework/pull/7516
    and DOT's OAuth2Authentication gets updated to add openapi security schemes and security requirement objects.
    """
    openapi_security_scheme_name = 'oauth2ForYou'

    @classmethod
    def openapi_security_scheme(cls):
        # N.B. Swagger UI still does not support OIDC, so always use OAuth2:
        scheme = {
            cls.openapi_security_scheme_name: {
                'type': 'oauth2',
                'description': 'OAuth 2.0 authentication',
            }
        }
        flows = {}
        if 'authorization_code' in settings.OAUTH2_CONFIG['grant_types_supported']:
            flows['authorizationCode'] = {
                'authorizationUrl': settings.OAUTH2_CONFIG['authorization_endpoint'],
                'tokenUrl': settings.OAUTH2_CONFIG['token_endpoint'],
                'refreshUrl': settings.OAUTH2_CONFIG['token_endpoint'],
                'scopes': {s: s for s in settings.OAUTH2_CONFIG['scopes_supported']}}
        if 'implicit' in settings.OAUTH2_CONFIG['grant_types_supported']:
            flows['implicit'] = {
                'authorizationUrl': settings.OAUTH2_CONFIG['authorization_endpoint'],
                'scopes': {s: s for s in settings.OAUTH2_CONFIG['scopes_supported']}}
        if 'client_credentials' in settings.OAUTH2_CONFIG['grant_types_supported']:
            flows['clientCredentials'] = {
                'tokenUrl': settings.OAUTH2_CONFIG['token_endpoint'],
                'refreshUrl': settings.OAUTH2_CONFIG['token_endpoint'],
                'scopes': {s: s for s in settings.OAUTH2_CONFIG['scopes_supported']}}
        if 'password' in settings.OAUTH2_CONFIG['grant_types_supported']:
            flows['password'] = {
                'tokenUrl': settings.OAUTH2_CONFIG['token_endpoint'],
                'refreshUrl': settings.OAUTH2_CONFIG['token_endpoint'],
                'scopes': {s: s for s in settings.OAUTH2_CONFIG['scopes_supported']}}
        scheme[cls.openapi_security_scheme_name]['flows'] = flows

        # TODO: add JWT and SAML2 bearer

        # content = []
        # permission_classes can be a direct list of classes, or instances of Operands, etc.
        # for perm in cls.view.permission_classes:
        #     if (isinstance(perm(), TokenMatchesOASRequirements)
        #             or cls._drf_conditional_contains(perm(), TokenMatchesOASRequirements)
        #             or cls._rest_cond_contains(perm(), TokenMatchesOASRequirements)):
        #         alt_scopes = cls.view.required_alternate_scopes
        #         if method not in alt_scopes:
        #             continue
        #         for scopes in alt_scopes[method]:
        #             content.append({'oauth': scopes})
        #
        return scheme

    @classmethod
    def openapi_security_requirement(cls, view, method):
        """
        OAuth2 is the only OAS security requirement object that fills in the list of required scopes
        :param view: used to get to the required_alternate_scopes attribute
        :param method: key for required_alternate_scopes
        :return:
        """
        scopes = []
        if hasattr(view, 'required_alternate_scopes'):
            if method in view.required_alternate_scopes:
                for alt in view.required_alternate_scopes[method]:
                    scopes.append({cls.openapi_security_scheme_name: alt})
        return scopes


class MyBasicAuth(BasicAuthentication):
    """
    demonstrate customizing the OAS security scheme name, once DRF 3.13 adds this functionality.
    """
    openapi_security_scheme_name = 'FooBar'


class SchemaGenerator(JSONAPISchemaGenerator):
    """
    Extend the schema to include some documentation, servers and override not-yet-implemented security.
    """
    def get_schema(self, request, public):
        schema = super().get_schema(request, public)
        schema['info'] = {
            'version': __version__,
            'title': __title__,
            'description':
                '![alt-text](https://cuit.columbia.edu/sites/default/files/logo/CUIT_Logo_286_web.jpg "CUIT logo")'
                '\n'
                '\n'
                '\n'
                'A sample API that uses courses as an example to demonstrate representing\n'
                '[JSON:API 1.0](http://jsonapi.org/format) in the OpenAPI 3.0 specification.\n'
                '\n'
                '\n'
                'See [https://columbia-it-django-jsonapi-training.readthedocs.io]'
                '(https://columbia-it-django-jsonapi-training.readthedocs.io)\n'
                'for more about this.\n'
                '\n'
                '\n' + __copyright__ + '\n',
            'contact': {
                'name': __author__
            },
            'license': {
                'name': __license__,
                'url': __license_url__
            }
        }
        schema['servers'] = [
            {'url': 'http://localhost:8000', 'description': 'local dev'},
            {'url': 'https://localhost', 'description': 'local docker'},
            {'url': 'https://ac45devapp01.cc.columbia.edu', 'description': 'demo'},
            {'url': '{serverURL}', 'description': 'provide your server URL',
             'variables': {'serverURL': {'default': 'http://localhost:8000'}}}
        ]

        # temporarily add securitySchemes until implemented upstream
        if 'securitySchemes' not in schema['components']:
            schema['components']['securitySchemes'] = {
                'basicAuth': {
                    'type': 'http',
                    'scheme': 'basic',
                    'description': 'basic authentication',
                },
                'sessionAuth': {
                    'type': 'apiKey',
                    'in': 'cookie',
                    'name': 'JSESSIONID',
                    'description': 'Session authentication'
                },
                'oauth-test': {
                    'type': 'oauth2',
                    'description': 'test OAuth2 service',
                    'flows': {
                        'authorizationCode': {
                            'authorizationUrl': 'https://oauth-test.cc.columbia.edu/as/authorization.oauth2',
                            'tokenUrl': 'https://oauth-test.cc.columbia.edu/as/token.oauth2',
                            'scopes': {
                                'auth-columbia': 'Columbia UNI login',
                                'create': 'create',
                                'read': 'read',
                                'update': 'update',
                                'delete': 'delete',
                                'openid': 'disclose your identity',
                                'profile': 'your user profile',
                                'email': 'your email address',
                                'https://api.columbia.edu/scope/group': 'groups you are a member of',
                                'demo-django-jsonapi-training-sla-bronze':
                                    'permitted to access the django-jsonapi-training demo: 1 request per second',
                                'demo-django-jsonapi-training-sla-update':
                                    'permitted to update the django-jsonapi-training resources'
                             }
                        }
                    }
                }
            }

        # temporarily add default security object at top-level
        if 'security' not in schema:
            schema['security'] = [
                {'basicAuth': []},
                {'sessionAuth': []},
                {'oauth-test': [['auth-columbia', 'openid', 'https://api.columbia.edu/scope/group']]}
            ]

        return schema
