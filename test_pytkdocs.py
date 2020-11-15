import os
import sys
import json
import django
from pytkdocs.cli import process_config

# reproduce "AttributeError: 'ManyRelatedField' object has no attribute 'metadata'"

input = """{
  "objects": [
    {
      "path": "myapp.serializers.CourseSerializer",
      "filters": [
        "!^_[^_]"
      ]
    }
  ]
}
"""

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "training.settings")
django.setup()
print(process_config(json.loads(input)))
