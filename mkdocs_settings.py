# This is how to get mkautodoc to run django.setup()
# kudos to @jlelanche: https://github.com/tomchristie/mkautodoc/issues/16
import os
import django  # noqa

setup = None

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "training.settings")
django.setup()
    
