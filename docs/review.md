# Review: git, Python, JSON

Some of us have attended in-house training on using git and Python developer training, with some exposure
to both the Flask and Django frameworks.

## Git

Make sure you know how to [git](https://git-scm.com) clone, checkout, add, commit, push

## Python & Django

MVC: [Model-View-Controller](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
(and [Django's weird terminology](https://docs.djangoproject.com/en/stable/faq/general/#django-appears-to-be-a-mvc-framework-but-you-call-the-controller-the-view-and-the-view-the-template-how-come-you-don-t-use-the-standard-names))

How to start a Django project and an app within the project: `django-admin startproject` and `django-admin startapp`.

Database persistance: models.py

Examples will follow.

## Javascript Object Notation (JSON)

JSON is the machine-readable de-facto standard for serializing data over
the web, supplanting XML, HTML, etc.

- Serialization of objects (for transmission across the net or sharing as documents).
- Simpler than XML: maps directly to programming language data structures.
- Human readable/writeable.

### JSON data types

All JSON data types are represented as strings in a JSON-encoded (serialized)
document but they map into common programming language datatypes (such
as in Javascript).

-  **strings** `"hello, world"`
-  **numbers** `1, 5.6, 1.3E22`
-  **boolean** - `true/false`
-  **null**
-  **object** - unordered set of key/value pairs, where the value can be of any type:
   ```json
   {"given": "Alan", "surname": "Crosswell", "age": 59, "likes": ["pizza", "xiao long bao"]}
   ```
-  **array** - ordered list of any types:
   ```json
   [1, 2, "three", {"color": "red"}, ["a", "b", null, true]]
   ```

### (De)serializing JSON (to)from Python variables: a simple Python app

```python
#!/usr/bin/env python
import json
from pprint import pprint

# json_serialized: "on the wire" string representation:
json_serialized = '[1,2,"three",{"color":"red"},["a","b",null,true]]'
print("JSON serialized:", json_serialized)
# json_deserialized: converted to Python-native variables
json_deserialized = json.loads(json_serialized)
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

### Footnote: Geezer history of serialization

Data in "machine" format is represented in unique ways depending on the hardware architecture.
For instance, integers can have an 8, 16, 32, or 64 bit
[2's-complement](https://www.cs.cornell.edu/~tomf/notes/cps104/twoscomp.html)
representation. Floating point numbers can be 32, 64 or 128-bits using representations
that are vendor-proprietary or perhaps
[IEEE floating point](https://www.cs.cornell.edu/~tomf/notes/cps104/floating.html).
Furthermore, the order of bytes within words can be
[big- or little-endian](https://chortle.ccsu.edu/AssemblyTutorial/Chapter-15/ass15_3.html).

When early computer networks were created among heterogenous systems, their
architectural differences were significant and standards were created
to move these data "across the wire" -- as a serial stream of bits --
and reconstruct them on the other end. Some of these early versions
include [ntohs](https://linux.die.net/man/3/ntohs) and so on which
converted between network and host byte order.

Later on, higher-level representations such as
[ASN.1](https://en.wikipedia.org/wiki/Abstract_Syntax_Notation_One)
were developed to similarly serialize/deserialize more complex objects using
a variety of encoding rules such as
[BER](https://en.wikipedia.org/wiki/X.690#BER_encoding).

The problem with all these binary encodings is that a human can't
decode them by just looking at them. As storage and networks became
cheaper and faster, plain text string serializations, based on text markup
languages, became popular, including XML (maybe not so easy:-) and, later,
JSON.
One of the things that has made JSON so popular is it is really easy
for a person to read and write.

Of course, the pendulum swings back, the amounts of data exchanged over
the network become massive, and some compact binary serialization
formats are back such as [Avro](https://en.wikipedia.org/wiki/Apache_Avro) --
which looks a lot like ASN.1 BER, DER and so on!

