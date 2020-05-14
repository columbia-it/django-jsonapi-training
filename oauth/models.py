from django.db import models
from oauth2_provider import models as oauth2_models


class MyAccessToken(oauth2_models.AbstractAccessToken):
    """
    extend the AccessToken model with the external userinfo server response
    """
    class Meta(oauth2_models.AbstractAccessToken.Meta):
        swappable = "OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL"

    userinfo = models.TextField(null=True, blank=True)


class MyRefreshToken(oauth2_models.AbstractRefreshToken):
    """
    extend the AccessToken model with the external introspection server response
    """
    class Meta(oauth2_models.AbstractRefreshToken.Meta):
        swappable = "OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL"


class MyApplication(oauth2_models.AbstractApplication):
    class Meta(oauth2_models.AbstractApplication.Meta):
        swappable = "OAUTH2_PROVIDER_APPLICATION_MODEL"
