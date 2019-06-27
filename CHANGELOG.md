# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased] - YYYY-MM-DD 

### Added

### Deprecated

### Changed

### Fixed

## [0.2.5] - 2019-06-27

### Added
- Automated OAS 3.0 schema document generation
- Added some model field validators

## [0.2.4] - 2018-04-26

### Added
- `jsonapi_demo_cli` command-line demonstration client.
- docker build
- OAS 3.0 [schema](docs/schemas/myapp.yaml)
- Added Swagger-UI at /openapi per [this article](https://dev.to/matthewhegarty/swaggerui-inside-django-rest-framework-1c2p)

### Deprecated

### Changed

### Fixed
- browseable api for courses raised an exception when related course was none.
- upgrade to Django 2.1.7 due to CVE-2019-6975.
- `GET /people/?filter[search]=...` 500 error.


## [0.2.3] - 2018-12-06

### Added
- Added a Person model
- Documentation is now available at https://columbia-it-django-jsonapi-training.readthedocs.io

### Changed
- Instructor model is now OneToOne with Person model.

### Fixed
- I misunderstood one of the SQL Server errors as complaining about a column name when it wasn't.
  This is fixed with migration 0007....

## [0.2.2] - 2018-12-03

### Added
- sphinx RTD configuration:
  - Run `tox` and then `open docs/build/html/index.html` in your local browser.
  - MyApp API autodoc.

### Deprecated
- No longer need `myapp/overridden_migrations` (see Fixed).

### Changed
- Split outline.md into individual chapter files:
  See [index.md](index.md). 

### Fixed
- created [PR](https://github.com/michiya/django-pyodbc-azure/pull/189) 
  for `django-pyodbc-azure` that elminates need for Microsoft SQL Server workarounds.

## [0.2.1] - 2018-11-20

### Added
- Workarounds for Microsoft SQL Server
  - TextFields can't be unique. Use Charfield.
  - "name" is a reserved word. Change the `db_column` so that we can keep using it in our code.
  - Can't change AutoField to BigAutoField.
  - Non-ANSI SQL implementation of NULL UNIQUE
  See the [docs](docs/outline.md#advanced-topic-sql-server-workarounds).

## [0.2.0] - 2018-11-14

### Added
- Instructor Model with ManyToMany relationship to CourseTerm.
  See [docs](docs/outline.md#another-modification-add-an-instructor-model-and-additional-relationship)

## [0.1.1] - 2018-11-09

### Added
- Document [Modifying our DJA Project](docs/outline.md#modifying-our-dja-project) with `CourseTerm` fix as the example.

### Fixed
- Make `CourseTerm.term_identifier` unique, char(14) and fix fixtures, etc. to match.

## [0.1.0] - 2018-10-31

### Added

- Initial release
