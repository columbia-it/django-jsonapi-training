from rest_framework.management.commands.generateschema import \
    Command as DRFCommand

from myapp.schemas.jsonapi import JSONAPISchemaGenerator

# see https://docs.djangoproject.com/en/2.2/howto/custom-management-commands/#overriding-commands
# to make this override the DRF version


class Command(DRFCommand):
    help = "Generates jsonapi.org schema for project."

    def get_generator_class(self):
        return JSONAPISchemaGenerator
