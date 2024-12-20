from drf_spectacular.extensions import OpenApiAuthenticationExtension


class DjangoOAuthToolkitScheme(OpenApiAuthenticationExtension):
    target_class = 'oauth2_provider.contrib.rest_framework.OAuth2Authentication'
    name = 'oauth2'

    def get_security_requirement(self, auto_schema):
        """
        Generate the OAS
        [Oauth2 security requirement object](https://spec.openapis.org/oas/latest#oauth2-security-requirement).

        Looks through the view permissions for relevent OAuth2 permission classes such as TokenMatchesOASRequirements
        in order to generate a list of alternative required scopes.

        TODO: Better deal with hierarchical (AND, OR) permissions.
        """
        from oauth2_provider.contrib.rest_framework import (IsAuthenticatedOrTokenHasScope, TokenHasScope,
                                                            TokenMatchesOASRequirements)
        view = auto_schema.view
        request = view.request

        for permission in auto_schema.view.get_permissions():
            if isinstance(permission, TokenMatchesOASRequirements):
                alt_scopes = permission.get_required_alternate_scopes(request, view)
                alt_scopes = alt_scopes.get(auto_schema.method, [])
                return [{self.name: group} for group in alt_scopes]
            if isinstance(permission, IsAuthenticatedOrTokenHasScope):
                return {self.name: TokenHasScope().get_scopes(request, view)}
            if isinstance(permission, TokenHasScope):
                # catch-all for subclasses of TokenHasScope like TokenHasReadWriteScope
                return {self.name: permission.get_scopes(request, view)}
            # deal with hierarchical boolean permissions.
            scopes = getattr(view, "required_alternate_scopes")
            if scopes is None:
                scopes = getattr(view, "required_scopes")  # try for required_scopes
                return {self.name: scopes if scopes else []}
            return [{self.name: a} for a in scopes[auto_schema.method]]

    def get_security_definition(self, auto_schema):
        """
        Render the securitySchemes for our oauth2 service.
        """
        from drf_spectacular.settings import spectacular_settings
        from oauth2_provider.scopes import get_scopes_backend

        flows = {}
        for flow_type in spectacular_settings.OAUTH2_FLOWS:
            flows[flow_type] = {}
            if flow_type in ('implicit', 'authorizationCode'):
                flows[flow_type]['authorizationUrl'] = spectacular_settings.OAUTH2_AUTHORIZATION_URL
            if flow_type in ('password', 'clientCredentials', 'authorizationCode'):
                flows[flow_type]['tokenUrl'] = spectacular_settings.OAUTH2_TOKEN_URL
            if spectacular_settings.OAUTH2_REFRESH_URL:
                flows[flow_type]['refreshUrl'] = spectacular_settings.OAUTH2_REFRESH_URL
            scope_backend = get_scopes_backend()
            flows[flow_type]['scopes'] = scope_backend.get_all_scopes()

        return {
            'type': 'oauth2',
            'flows': flows
        }
