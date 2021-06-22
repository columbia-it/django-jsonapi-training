from oauth2_provider.oauth2_validators import OAuth2Validator


class CustomOAuth2Validator(OAuth2Validator):
    """
    Extend the ID Token and Userinfo claims
    """
    def get_additional_claims(self, request):
        """
        Return additional ID Token Claims based on the OIDC scope claims.
        Args:
            request:

        Returns:
            dict of additional claims
        """
        claims = {
            "sub": request.user.username
        }
        if 'profile' in request.scopes:
            claims["given_name"] = request.user.first_name
            claims["family_name"] = request.user.last_name
            claims["name"] = ' '.join([request.user.first_name, request.user.last_name])
        if 'email' in request.scopes:
            claims["email"] = request.user.email
        if 'https://api.columbia.edu/scope/group' in request.scopes:
            claims['https://api.columbia.edu/claim/group'] = ' '.join([g.name for g in request.user.groups.all()])
        return claims

    def get_userinfo_claims(self, request):
        """
        Return additional Userinfo claims
        Args:
            request:

        Returns: userinfo dict
        """
        claims = super().get_userinfo_claims(request)
        # This version of request seems to only have the 'openid' scope. That's probably a bug.
        # additional_claims = self.get_additional_claims(request)
        # for now kludge it to provide all the stuff while we investigate if this is a bug:
        # https://github.com/jazzband/django-oauth-toolkit/issues/952
        request.scopes = request.access_token.scope.split()
        additional_claims = self.get_additional_claims(request)
        return {**claims, **additional_claims}
