## Documenting the API in OAS 3.0

The [Open API Specification](https://github.com/OAI/OpenAPI-Specification/versions/3.0.0.md)
(OAS 3.0), a follow-on to Swagger 2.0 which merges in many of the
modeling features of
[RAML](https://raml.org/)
1.0, allows us to model and document our APIs
in a machine- and human-readable format. See the following example.
OAS 3.0 has become the standard machine-readable representation of API schemas.

DRF has _begun_ adding
[OAS 3.0](https://www.django-rest-framework.org/community/3.9-announcement/#built-in-openapi-schema-support)
support and will likely need some DJA enhancements before it is ready to automate generating a schema document.
But it looks like the ability to generate at least a rudimentary OAS schema starting from Models, Views
and Serializers may soone be a relaity.

### Why an OAS 3.0 Schema?

Having a standardized schema document enables API consumer and producer developers to formally agree on the
API details in an automated way, providing tools for developers to perform basic data input validation
and to provide developer documentation and the familiar swagger "Try it!" functionality.

![alt-text](./media/swagger-ui.png "screenshot of Swagger UI")

### Experiments with OpenAPI Schema documentation, validation and mocking tools

While "waiting" on automated OAS schema generation, I've been experimenting with manually coding a schema
to get a feeling for the value of eventually having automated schema generation.

#### Composing the OAS Schema with external references.

To make things DRYer, the OAS schema can be decomposed into shareable pieces that are referenced via the `$ref` tag.
These can be files in the same directory as the schema file or reachable via http references.  For example,
replace `"$ref": "#/components/schemas/CourseAttributes"` with 
`"$ref": "Course.json#/definitions/CourseAttributes"` or
`"$ref": "http://www.columbia.edu/~alan/schemas/sas/Course.json#/definitions/CourseAttributes"`.

#### The jsonapi OAS schema

This [jsonapi schema include file](http://www.columbia.edu/~alan/schemas/common/jsonapi.yaml)
is referenced by `myapp.yaml` and contains the {json:api} common definitions that myapp references.

#### Myapp's OAS 3.0 schema with swagger Try It functionality

This hand-written schema actually works and allows "Try It!" functionality with the following caveats:
- Change the API port to 9123 in PyCharm since the default port for swagger-ui-watcher is 8000.
- OAuth2 clients need to be configured that include these request_uris:
  - http://127.0.0.1/oauth2-redirect.html
  - http://localhost/oauth2-redirect.html

Both Basic Auth and OAuth2 logins are supported.

See `docs/schemas/myapp.yaml`

Here are some abbreviated snippets of myapp.yaml:
```yaml
openapi: 3.0.2
info:
  version: 1.0.0
  title: 'django-jsonapi-training example'
  description: >-
    A sample API that uses courses as an example to demonstrate representing
    [JSON:API 1.0](http://jsonapi.org/format) in the OpenAPI 3.0 specification.
  contact:
    name: Alan Crosswell
    email: alan@columbia.edu
    url: 'http://www.columbia.edu/~alan'
  license:
    name: Apache 2.0
    url: 'https://www.apache.org/licenses/LICENSE-2.0.html'
servers:
  - url: 'http://localhost:9123/v1'
paths:
  /courses/:
    get:
      description: Returns a collection of courses
      operationId: find courses
      security:
        - basicAuth: []
        - oauth-dev: [auth-columbia, read]
      responses:
        '200':
          description: course response
          content:
            application/vnd.api+json:
              schema:
                $ref: '#/components/schemas/CourseCollection'
components:
  securitySchemes:
    basicAuth:
      type: http
      scheme: basic
    oauth-dev:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://oauth-dev.cuit.columbia.edu:8443/as/authorization.oauth2
          tokenUrl: https://oauth-dev.cuit.columbia.edu:8443/as/token.oauth2
          scopes:
            "auth-columbia": Columbia UNI login
            create: create
            read: read
            update: update
            delete: delete
            openid: disclose your identity
            profile: your user profile
            email: your email address
            "https://api.columbia.edu/scope/group": groups you are a member of
            "demo-netphone-admin": Administrative access to netphone resources
  schemas:
  # ...
    CourseCollection:
      type: array
      items:
        $ref: '#/components/schemas/CourseItem'
    CourseItem:
      allOf:
        - $ref: 'http://www.columbia.edu/~alan/schemas/common/jsonapi.yaml#/components/schemas/resource'
        - type: object
          properties:
            attributes:
              $ref: '#/components/schemas/CourseSchema'
            relationships:
              $ref: '#/components/schemas/CourseRelationships'
```

#### swagger-editor

Swagger-editor installs as a
[docker container](https://github.com/swagger-api/swagger-editor#docker)
and then runs an in-browser schema editor. It's main failings are:
- the editor stores files in the container so you have to explicitly export files to the local filesystem.
- it does not follow network `$ref`s (e.g. to `http://www.columbia.edu/~alan/schemas/sas/Course.json`)


#### swagger-ui-watcher

Swagger-ui-watcher lets you edit the API definition in your favorite text editor and updates the browser view
dynamically as the file changes. Otherwise it looks just like swagger-editor. It also properly follows
`$ref` network URIs.

To run it:

`npm install swagger-ui-watcher -g` then `swagger-ui-watcher ./openapi.yaml`

You can use `swagger-ui-watcher` to "bundle" you app's OAS schema with the external schemas that it
references. The bundled output file is always a JSON document.

```
schemas$ swagger-ui-watcher -b myapp.json myapp.yaml
```

#### Schema validation with apistar

While the swagger-ui packages will validate a schema, with error messages popping up in the browser window,
you can also do command-line OAS schema validation with a number of tools. A cool new one is
[apistar](https://docs.apistar.com/):

```text
docs$ pip install apistar
docs$ apistar validate  --path schemas/myapp.json --format openapi
✓ Valid OpenAPI schema.
```

#### Working around a missing oauth2-redirect.html in swagger-editor and swagger-ui-watcher

The swagger-editor distribution package (and therefore swagger-ui-watcher as well) currently fails to finish a proper OAuth2
login because a 404 not found happens for a [missing /oauth2-redirect.html](https://github.com/swagger-api/swagger-editor/issues/1969).

##### swagger-ui-watcher

The (hopefully temporary) [workaround](https://github.com/moon0326/swagger-ui-watcher/issues/31#issuecomment-476799840)
for swagger-ui-watcher is to grab a copy of
[oauth2-redirect.html](https://github.com/swagger-api/swagger-ui/blob/master/dist/oauth2-redirect.html)
and:
```text
cp oauth2-redirect.html /usr/local/lib/node_modules/swagger-ui-watcher/node_modules/swagger-editor-dist/
```

##### swagger-editor docker

```text
swagger-editor$ docker exec -it heuristic_mirzakhani sh
/ # cd /usr/share/nginx/html/
/usr/share/nginx/html # # I had a copy already salted away ...
/usr/share/nginx/html # mv oauth2-redirect.htmlx oauth2-redirect.html
/usr/share/nginx/html # exit
swagger-editor$ docker restart heuristic_mirzakhani
heuristic_mirzakhani
```

#### Some issues I have with OAS

It's not a DRY as I want it to be:

* `$ref` can't generally be used to set some values and then extend them.
* There are no parameterized macros like in
  [RAML](https://github.com/raml-org/raml-spec/blob/master/versions/raml-10/raml-10.md#resource-type-and-trait-parameters).

As such, OAS is more suited as a machine-generated file format than something a human should be expected to compose.
To get any kind of reuse out of an OAS document, it will need to be pre-processed with something like
[m4](https://www.gnu.org/software/m4) to basically add parameter substitutions.
