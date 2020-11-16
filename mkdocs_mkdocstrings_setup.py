# mkdocstrings plugin setup
import os
import pip
pip._internal.main(["install", "-v", "-r", "docs/requirements-mkdocs.txt"])
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "training.settings")
django.setup()

