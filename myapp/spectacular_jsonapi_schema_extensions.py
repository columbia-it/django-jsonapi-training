import logging
log = logging.getLogger(__name__)

from rest_framework_json_api.views import ModelViewSet
from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema

log.debug(f"{__name__} here")


class MyModelViewSetExtension(OpenApiViewExtension):
    target_class = "rest_framework_json_api.views.ModelViewSet"


    def view_replacement(self):
        @extend_schema(
            summary="Custom summary for MyModelViewSet",
            description="This is a custom description for MyModelViewSet.",
            tags=["mymodelviewset", "custom"],
        )

        def custom_view(*args, **kwargs):
            return self.target_class.as_view({'get': 'list'})(*args, **kwargs)

        return custom_view

