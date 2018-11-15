# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased] - YYYY-MM-DD 

### Added

### Deprecated

### Changed

### Fixed

## [0.2.0] - 2018-11-14

### Added
- Instructor Model with ManyToMany relationship to CourseTerm.
  See [docs](http://localhost:6419/docs/outline.md#another-modification-add-an-instructor-model-and-additional-relationship)

## [0.1.1] - 2018-11-09

### Added
- Document [Modifying our DJA Project](docs/outline.md#modifying-our-dja-project) with `CourseTerm` fix as the example.

### Fixed
- Make `CourseTerm.term_identifier` unique, char(14) and fix fixtures, etc. to match.

## [0.1.0] - 2018-10-31

### Added

- Initial release