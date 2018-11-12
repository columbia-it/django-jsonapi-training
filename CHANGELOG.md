# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Note that in line with [Django REST Framework policy](http://www.django-rest-framework.org/topics/release-notes/),
any parts of the framework not mentioned in the documentation should generally be considered private API, and may be subject to change.

## [0.1.1] - 2018-11-09

### Added
- Document [Modifying our DJA Project](docs/outline.md#modifying-our-dja-project) with `CourseTerm` fix as the example.

### Deprecated

### Changed

### Fixed
- Make `CourseTerm.term_identifier` unique, char(14) and fix fixtures, etc. to match.

## [0.1.0] - 2018-10-31

### Added

- Initial release
