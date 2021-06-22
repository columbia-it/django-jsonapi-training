from django.db import models
from oauth2_provider import models as oauth2_models


class MyAccessToken(oauth2_models.AbstractAccessToken):
    """
    extend the AccessToken model with the external userinfo server response
    """
    class Meta(oauth2_models.AbstractAccessToken.Meta):
        swappable = "OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL"

    userinfo = models.TextField(null=True, blank=True)


# It's not clear why, but there's some interdependency between the models that
# seems to require creating swappable models even when no changes are needed
# to them:
class MyIDToken(oauth2_models.AbstractIDToken):
    class Meta(oauth2_models.AbstractIDToken.Meta):
        swappable = "OAUTH2_PROVIDER_ID_TOKEN_MODEL"


class MyRefreshToken(oauth2_models.AbstractRefreshToken):
    class Meta(oauth2_models.AbstractRefreshToken.Meta):
        swappable = "OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL"


class MyApplication(oauth2_models.AbstractApplication):
    class Meta(oauth2_models.AbstractApplication.Meta):
        swappable = "OAUTH2_PROVIDER_APPLICATION_MODEL"
