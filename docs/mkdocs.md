# Mkdocs Documentation

## About MkDocs

[MkDocs](https://mkdocs.readthedocs.io) is a general-purpose tool for generating
project documentation using Markdown files. 

## MkDocs vs. Sphinx

Sphinx is the initial tool I decided to use for documenting this project.
I've since been experimenting with the [Backstage](backstage.md) developer portal
which uses MkDocs for their [TechDocs](https://backstage.io/docs/features/techdocs/techdocs-overview)
tool so I figured I'd experiment with MkDocs.

A few pros and cons of MkDocs with the [mkdocstrings](https://pawamoy.github.io/mkdocstrings) plugin over Sphinx
with the [autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) extension:

### Pro

* Only uses Markdown. No more RsT, which is Python-specific, and kind of ugly.
  * In general, Markdown syntax is less cumbersome than RsT's.
    For example: `[sitename](url)` vs. `` `sitename <url>`_ ``.
* Works with Backstage TechDocs.
* Easier configuration in [`mkdocs.yml`]({{view_uri}}/mkdocs.yml)
  vs. [`docs/conf.py`]({{view_uri}}/docs/conf.py) 
* Extensible with many plugins including [macros](https://mkdocs-macros-plugin.readthedocs.io)
  which I use here to substitute the `view_uri` in references.

### Con

* ~~RsT markup in Python docstrings will have to be refactored to Markdown.~~
* Also extensible via plugins and with any Python code you care to add to `conf.py`.
* Alternatives to `apidoc` are not great. The closes seems to be 
  [`mkdocstrings`](https://pawamoy.github.io/mkdocstrings) which
  ~~[fails to work with some DRF components](https://github.com/pawamoy/mkdocstrings/issues/141).~~

## Converting this project to MkDocs

```text
# bring in requirements for my app (excepting the optional database):
-r../requirements-django.txt
# stuff needed for mkdocs documentation:
Markdown==3.2.2
mkdocs-techdocs-core==0.0.13
mkdocs-macros-plugin==0.4.20
mkdocstrings==0.13.6
mkdocs==1.1.2
```

* Use backstage.io's techdocs-core plugin which brings in several others.

* Use macros plugin as described above, including
  [this custom code]({{view_uri}}/mkdocs_macros_main.py) which:
  defines `view_uri` based on the git repo configuration.This requires adding `{{'{{'}}view_uri{{'}}'}}`
  in URL references in the various markdown files which previously didn't have
  any links. You can also use macros like `{{'{{'}}git.date{{'}}'}}` to show the repo
  date.
 
* Mkdocstrings for automated API documentation.

* In `mkdocs.yml` add the document hierarchy that is in `docs/index.rst`.

## Viewing MkDocs-generated content locally

This is easily accomplished:

```
tox -e livedocs  # and open http://localhost:9000
```

!!! Note
    The default port for `mkdocs serve` is 8000 which is also what we use for our django app.

## Publishing to RTD

[Readthedocs](https://readthedocs.io) easily supports both Sphinx and MkDocs through
a configuration file. Changing this project over required adding
[`.readthedocs.yaml`]({{view_uri}}/.readthedocs.yaml):

```yaml
# .readthedocs.yml
# Read the Docs configuration file
# See https://docs.readthedocs.io/en/stable/config-file/v2.html for details

# Required
version: 2

# Build documentation in the docs/ directory with Sphinx
# sphinx:
#   configuration: docs/conf.py

build:
  os: ubuntu-22.04
  tools:
    python: "3.12"

# Build documentation with MkDocs
mkdocs:
  configuration: mkdocs.yml

# Optionally set the version of Python and requirements required to build your docs
python:
  install:
    - requirements: docs/requirements-mkdocs.txt
```

