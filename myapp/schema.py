from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object

class MyAuthenticationSchemes(OpenApiAuthenticationExtension):
    """
    Make a list of securityScheme names and return a parallel list of definitions
    """
    target_class = "oauth2_provider.contrib.rest_framework.OAuth2Authentication"
    name = ["oauth2-test", "oauth2-prod", "oauth2-local"]


    def get_security_definition(self, auto_schema):
        # TODO -- flesh out Django-oauth-toolkit stuff
        # r = build_bearer_security_scheme_object(header_name="AUTHORIZATION",
        #                                         token_prefix="Bearer",)
        return [
            {
                "type": "oauth2",
                "description": "test OAuth2 service",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://oauth-test.cc.columbia.edu/as/authorization.oauth2",
                        "tokenUrl": "https://oauth-test.cc.columbia.edu/as/token.oauth2",
                        "scopes": {
                            "auth-columbia": "Columbia UNI login",
                            "create": "create",
                            "read": "read",
                            "update": "update",
                            "delete": "delete",
                            "openid": "disclose your identity",
                            "profile": "your user profile",
                            "email": "your email address",
                            "https://api.columbia.edu/scope/group": "groups you are a member of",
                            "demo-djt-sla-bronze": "permitted to access the django-jsonapi-training demo: 1 request per second",
                            "demo-djt-sla-update": "permitted to update the django-jsonapi-training resources",
                        }
                    }
                }
            },
            {
                "type": "oauth2",
                "description": "OAuth2 service",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://oauth.cc.columbia.edu/as/authorization.oauth2",
                        "tokenUrl": "https://oauth.cc.columbia.edu/as/token.oauth2",
                        "scopes": {
                            "auth-columbia": "Columbia UNI login",
                            "create": "create",
                            "read": "read",
                            "update": "update",
                            "delete": "delete",
                            "openid": "disclose your identity",
                            "profile": "your user profile",
                            "email": "your email address",
                            "https://api.columbia.edu/scope/group": "groups you are a member of",
                            "demo-djt-sla-bronze": "permitted to access the django-jsonapi-training demo: 1 request per second",
                            "demo-djt-sla-update": "permitted to update the django-jsonapi-training resources",
                        }
                    }
                }
            },
            {
                "type": "oauth2",
                "description": "local DOT OAuth2 service",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "http://localhost:8000/o/authorize/",
                        "tokenUrl": "http://localhost:8000/o/token/",
                        "scopes": {
                            "auth-columbia": "Columbia UNI login",
                            "create": "create",
                            "read": "read",
                            "update": "update",
                            "delete": "delete",
                            "openid": "disclose your identity",
                            "profile": "your user profile",
                            "email": "your email address",
                            "https://api.columbia.edu/scope/group": "groups you are a member of",
                            "demo-djt-sla-bronze":
                                "permitted to access the django-jsonapi-training demo: 1 request per second",
                            "demo-djt-sla-update":
                                "permitted to update the django-jsonapi-training resources"
                        }
                    }
                }
            },
        ]


def custom_postprocessing_hook(result, generator, request, public):
    """
    Customize the schema to include a selectable list of servers, including
    the option to supply your own custom server URL.
    """
    result["servers"] = [
        {'url': 'http://localhost:8000', 'description': 'local dev'},
        {'url': 'https://localhost', 'description': 'local docker'},
        {'url': 'https://ac45devapp01.cc.columbia.edu', 'description': 'demo'},
        {'url': '{serverURL}', 'description': 'provide your server URL',
         'variables': {'serverURL': {'default': 'http://localhost:8000'}}}
    ]
    return result
