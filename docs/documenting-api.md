## Documenting the API in OAS 3.0

The [Open API Specification](https://github.com/OAI/OpenAPI-Specification/versions/3.0.0.md)
(OAS 3.0), a follow-on to Swagger 2.0 which merges in many of the
modeling features of RAML 1.0, allows us to model and document our APIs
in a machine- and human-readable format. See the following example.

*OAS 3.0 support is still evolving (the standard is just about one year
old) so many of the tools that work for Swagger 2.0 are not yet ready.
These tools (see [https://swagger.io](https://swagger.io))
will help clients build their apps.*

```yaml
openapi: "3.0.0"
info:
  title: courses
  version: v1
components:
  securitySchemes:
    course_auth:
      type: oauth2
      flows:
        implicit:
          authorizationUrl: https://oauth.cc.columbia.edu/as/authorization.oauth2
      scopes:
        create: create a new course
        read: read about a course
        update: update an existing course
        delete: delete a course
        demo-netphone-admin: sample enterprise scope
paths:
  /courses:
    get:
      security:
        - course_auth: [auth-columbia, read]
        - course_auth: [auth-none, read]
      responses:
        '200':
           description: A list of courses.
    post:
      security:
        - course_auth: [auth-columbia, demo-netphone-admin, create]
        - course_auth: [auth-none, demo-netphone-admin, create]
      responses:
        '201':
           description: new course added
    patch:
      security:
        - course_auth: [auth-columbia, demo-netphone-admin, create]
        - course_auth: [auth-none, demo-netphone-admin, create]
      responses:
        '204':
          description: course updated
    delete:
      security:
        - course_auth: [auth-columbia, demo-netphone-admin, create]
        - course_auth: [auth-none, demo-netphone-admin, create]
      responses:
        '200':
          description: course deleted
```

TODO: DRF 3.9 adds the beginnings of support to generate an OAS schema, eventually replacing `coreapi` but it
currently breaks when trying to render DJA's `ResourceRelatedField`.
