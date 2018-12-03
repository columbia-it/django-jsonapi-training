## Review of key concepts from Python and Git training

-   MVC: Model-View-Controller
    ([and Django's weird terminology](https://docs.djangoproject.com/en/2.0/faq/general/#django-appears-to-be-a-mvc-framework-but-you-call-the-controller-the-view-and-the-view-the-template-how-come-you-don-t-use-the-standard-names))
-   how to start a project and an app
-   models.py
-   git clone, checkout, add, commit, push

### Javascript Object Notation (JSON)

JSON is the machine-readable de-facto standard for serializing data over
the web, supplanting XML, HTML, etc.

Serialization of objects (for transmission across the net/sharing as
documents).

Simpler than XML: maps directly to programming language data structures.

Human readable/writeable.

### JSON data types

-   **strings** "hello, world"
-   **numbers** 1, 5.6, 1.3E22
-   **boolean** - true/false
-   **null**
-   **object** - unordered set of key/value pairs:
    {"given": "Alan", "surname": "Crosswell", "age": 59}
-   **array** - ordered list of any types:
    [1, 2, "three", {"color": "red"}, ["a", "b", null, true]]

### (De)serializing JSON (to)from Python variables: a simple Python app

```python
#!/usr/bin/env python
import json
from pprint import pprint

json_serialized = '[1,2,"three",{"color":"red"},["a","b",null,true]]'
json_deserialized = json.loads(json_serialized)
print("JSON serialized:", json_serialized)
print("Python object:")
pprint(json_deserialized)
for item in json_deserialized:
    print("item:",item)
print(json_deserialized[3]['color'])
```

```bash
$ python3 json-example.py
JSON serialized: [1,2,"three",{"color":"red"},["a","b",null,true]]
Python object:
[1, 2, 'three', {'color': 'red'}, ['a', 'b', None, True]]
item: 1
item: 2
item: three
item: {'color': 'red'}
item: ['a', 'b', None, True]
red
```

