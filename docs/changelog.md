# Documentation Revision History

Since this project is primarily documentation for training purposes, this Changelog
documents the changes to the docs. See the project CHANGELOG for changes to the demo app.

## 2022-12-23
- Get mkdocs documentation back working and deprecate sphinx. Still need to update the docs!
- Add documentation for using Django OAuth Toolkit (DOT) as the OAuth AS.
- You can now do `(env) django-training$ ./manage.py loaddata myapp/fixtures/*` to create the superuser,
  regular test users, various OAuth2 client identities and load both test data and a large course
  inventory dataset of about 4K Courses and CourseTerms.

## 2021-06-25
- Disable API autodocumentation for the time being due to mkdocstrings/pytkdocs version issues.
- Document using DOT's 1.5.0's new OIDC support.

## 2020-11-17
- Switched documentation from Sphinx to MkDocs.
- Added [Backstage](/backstage) developer portal info.

## 2020-11-05
- Added automated OpenAPI schema generation now that it is supported by DJA.

## 2020-05-14
- Reorganized material to introduce OAuth 2.0 prior to diving in to building the app.
- Removed enterprise down-scoping which is replaced with OIDC Claims.
- Purge references to third party Microsoft SQL Server since it is poorly supported and not a core
  [Django supported database](https://docs.djangoproject.com/en/3.0/ref/databases/).

## 2018-12-01
- Switch documentation over to Sphinx.

## 2018-11-20
- Kludges required when using sqlserver.

## 2018-11-15
- Add Instructor model.

## 2018-11-08
- Convert from google doc (to docx) to markdown with pandoc.
- Changes for DJA 2.6.0 for related_serializers.
- Miscellaneous cleanup and expansion of examples.
- prepare for initial github.com release.

## 2018-07-19
- Updates for added openid scopes and claims.

## 2018-06-14
- Improved documentation of Relationship & Related views.
- Tox, code coverage.
- More About Using OAuth 2.0
- refresh code examples.
