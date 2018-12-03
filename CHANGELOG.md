# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased] - YYYY-MM-DD 

### Added

### Deprecated

### Changed

### Fixed

## [0.2.2] - YYYY-MM-DD 

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
