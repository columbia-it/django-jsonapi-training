from django.conf import settings
# from drf_spectacular.extensions import OpenApiAuthenticationExtension
# from drf_spectacular.contrib.django_oauth_toolkit import DjangoOAuthToolkitScheme
from myapp.django_oauth_toolkit import DjangoOAuthToolkitScheme

# class MyAuthenticationSchemes(DjangoOAuthToolkitScheme):
#     """
#     Make a list of securityScheme names and return a parallel list of definitions
#     """
#     target_class = "oauth2_provider.contrib.rest_framework.OAuth2Authentication"
#     name = ["oauth2-test", "oauth2-prod", "oauth2-local"]


#     def get_security_definition(self, auto_schema):
#         # TODO -- flesh out Django-oauth-toolkit stuff
#         # N.B. see also spectacular_settings.SWAGGER_UI_OAUTH2_CONFIG, OAUTH2_FLOWS, etc.
#         # which will do most of this!
#         r = super().get_security_definition(auto_schema)
#         print(f"security definition: {r}")
#         return [
#             {
#                 "type": "oauth2",
#                 "description": "test OAuth2 service",
#                 "flows": {
#                     "authorizationCode": {
#                         "authorizationUrl": "https://oauth-test.cc.columbia.edu/as/authorization.oauth2",
#                         "tokenUrl": "https://oauth-test.cc.columbia.edu/as/token.oauth2",
#                         "scopes": {
#                             "auth-columbia": "Columbia UNI login",
#                             "create": "create",
#                             "read": "read",
#                             "update": "update",
#                             "delete": "delete",
#                             "openid": "disclose your identity",
#                             "profile": "your user profile",
#                             "email": "your email address",
#                             "https://api.columbia.edu/scope/group": "groups you are a member of",
#                             "demo-djt-sla-bronze": "permitted to access the django-jsonapi-training demo: 1 request per second",
#                             "demo-djt-sla-update": "permitted to update the django-jsonapi-training resources",
#                         }
#                     }
#                 }
#             },
#             {
#                 "type": "oauth2",
#                 "description": "OAuth2 service",
#                 "flows": {
#                     "authorizationCode": {
#                         "authorizationUrl": "https://oauth.cc.columbia.edu/as/authorization.oauth2",
#                         "tokenUrl": "https://oauth.cc.columbia.edu/as/token.oauth2",
#                         "scopes": {
#                             "auth-columbia": "Columbia UNI login",
#                             "create": "create",
#                             "read": "read",
#                             "update": "update",
#                             "delete": "delete",
#                             "openid": "disclose your identity",
#                             "profile": "your user profile",
#                             "email": "your email address",
#                             "https://api.columbia.edu/scope/group": "groups you are a member of",
#                             "demo-djt-sla-bronze": "permitted to access the django-jsonapi-training demo: 1 request per second",
#                             "demo-djt-sla-update": "permitted to update the django-jsonapi-training resources",
#                         }
#                     }
#                 }
#             },
#             {
#                 "type": "oauth2",
#                 "description": "local DOT OAuth2 service",
#                 "flows": {
#                     "authorizationCode": {
#                         "authorizationUrl": "http://localhost:8000/o/authorize/",
#                         "tokenUrl": "http://localhost:8000/o/token/",
#                         "scopes": {
#                             "auth-columbia": "Columbia UNI login",
#                             "create": "create",
#                             "read": "read",
#                             "update": "update",
#                             "delete": "delete",
#                             "openid": "disclose your identity",
#                             "profile": "your user profile",
#                             "email": "your email address",
#                             "https://api.columbia.edu/scope/group": "groups you are a member of",
#                             "demo-djt-sla-bronze":
#                                 "permitted to access the django-jsonapi-training demo: 1 request per second",
#                             "demo-djt-sla-update":
#                                 "permitted to update the django-jsonapi-training resources"
#                         }
#                     }
#                 }
#             },
#         ]


#     def get_security_requirement(self, autoschema):
#         r = super().get_security_requirement(autoschema)
#         print(f"security_requirement: {r}")
#         return r
