from django.apps import AppConfig


class MyappConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        # bring in the drf-spectacular schema extensions
        import myapp.schema  # noqa: E402
