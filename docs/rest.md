# HTTP and REpresentational State Transfer (REST)

## HTTP Requests and Responses

An HTTP request consists of a verb (HTTP method), scheme (http/https), server, port and
resource (noun), and query parameters.

e.g. A GET of `https://127.0.0.1:8000/api/widgets/123?sort=-name`
(using [Basic authentication](https://datatracker.ietf.org/doc/html/rfc7235)) is actually transmitted like this
after establishing a TCP connection to port 8000:

```text
GET /widgets/?sort=-name HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Basic YWRtaW46YWRtaW4xMjM=
User-Agent: curl/7.54.0
Accept: application/vnd.api+json
```

Common methods are:

| **HTTP Method**       | **Action**            | **Usual Status Codes** |
| :-------------------- | :-------------------- | :-------------------- |
| POST                  | create a new item under the resource collection URL.  | 201 Created           |
|                       |                       | 202 Accepted          |
|                       |                       | 204 No content        |
|                       |                       | 403 Forbidden         |
|                       |                       | 404 Not found         |
|                       |                       | 409 Conflict          |
| GET                   | read either a collection or item within a collection  | 200 OK                |
|                       |                       | 403, 404              |
| PATCH or PUT          | update by changing some (or all) the data for a resource | 200, 202, 204         |
|                       |                       | 403, 404, 409         |
| DELETE                | delete an item (or collection!)  | 200, 202, 204         |
|                       |                       | 403, 404, 409         |
| OPTIONS               | obtain metadata about a resource collection or item | 200                   |


### Request Body

Usually where longer form parameters or content is POSTed. The `Content-Type`
header specifies what kind of content is being POSTed, PATCHed or PUT.
For our purposes this will be `application/json` or a variant such as `application/vnd.api+json`
(which is used by [{json:api}](https://jsonapi.org)).

### Response Body

The response to the request, which can be empty (204 No Content)
looks like this, for example, for a 200 response:

```text
HTTP/1.1 200 OK
Date: Fri, 14 Dec 2018 16:26:02 GMT
Server: WSGIServer/0.2 CPython/3.6.6
Content-Type: application/vnd.api+json
Vary: Accept
Allow: GET, POST, HEAD, OPTIONS
X-Frame-Options: SAMEORIGIN
Content-Length: 74

{"data":{"type":"widgets","id": "123","attributes":{"name":"can opener"}}}
```

### Query Parameters

These are usually short parameters that somehow modify a request

Example: `GET /api/v1/widgets?sort=-name,+qty`

### Headers

The HTTP `Accept` header lists what (prioritized) content types the
requestor will accept. We'll keep it simple and only
accept one response type: `Accept: application/json`

The HTTP Content-Type header specifies the format of the response:
`Content-type: application/json`

### Authentication and Authorization

The HTTP `Authorization` header is commonly used for access control. There
are 3 main styles:

1. `Authorization: Bearer <token>` header -- used with OAuth 2 and
   REST APIs. Stateless.
2. `Authorization: Basic <b64-encoded-user:password>` header --
   Common for server-to-server, including REST. Stateless.
3. *Session* -- Used by conventional browser-based apps with a user
   at one end. Maintains state across multiple HTTP request/response
   iterations via session cookies (`Set-Cookie` response and `Cookie` request headers).

Our "real" apps will use Bearer tokens. For testing in Django, it can be
more convenient to use Basic auth as Bearer tokens have to be refreshed
from time-to-time. We'll see how to configure these soon.

## Characteristics of RESTful APIs

[Representational State Transfer (REST)](https://en.wikipedia.org/wiki/Representational_state_transfer)
is a core component of an HTTP-based object model style.

RESTful APIs, unlike SOAP APIs, use only the native HTTP methods as they were meant to be used.

* Object-Relational Model (ORM) API using HTTP
* Client-server - separation of concerns, allows independent evolution of components.
* Stateless - no session state maintained between requests
* Layered - Client/Server don't care if additional layers (e.g. caches,
  load balancers) are in between.
* Uniform interface:
  - Resource collections and items within collections: ID in URL
  - Use of HTTP request methods and responses as designed (contrasted with SOAP/WSDL)
* Idempotent (hopefully) - same request can be duplicated with equivalent result
* Cacheable - frequently referenced data can be cached to avoid
  unnecessary network traffic. Can happen at multiple levels (client,
  cache in front of server, cached in server, etc.)

**Proper** REST HTTP URLs are characterized by _resources_ and _resource collections_
which are plural nouns. The only verbs are the HTTP methods: GET, POST, DELETE, PATCH, PUT, etc.

For example:

`GET /v1/registrations` returns a collection of individual registrations each having an `<id>`.

`GET /v1/registrations/<id>` returns an individual registration.

`POST /v1/registrations` (with
a request body containing a JSON document with other information like the identity of the registrant)
results in a new registration object identified as:
`/v1/registrations/<id>`.

### HATEOAS: Hypermedia As The Engine Of Application State.

Given a starting URL, a client app *should* be able to discover everything it needs
without any separate external documentation of the interface.


### Avoid REST anti-patterns

It is unfortunately common to see non-RESTful patterns sneaking into what claim to be RESTful APIs. The most
common of these anti-patterns is turning a REST API endpoint into a SOAP-like endpoint by invoking
a remote method call. For example, `POST /v1/courses/01ca197f-c00c-4f24-a743-091b62f1d500/enroll`.
You can immediately tell this is an anti-pattern because "enroll" is used here as a verb
and RESTful resources should only be nouns.

### A good REST pattern

A RESTful approach to the above might be something along the lines of:
`POST /v1/registrations/` with a body containing:
```json
{
    "data": {
        "type": "registrations",
        "attributes": {
            "uni": "abc1234",
            "enrollment": "requested"
        },
        "relationships": {
            "courses": {
                "data": {
                        "type": "courses",
                        "id": "01ca197f-c00c-4f24-a743-091b62f1d500"
                }
            }
        }
    }
}
```

A side-effect of this data being added to the Registration Model would be to invoke the
enrollment process. This could be synchronous, returning a final `201 Created` status
or asynchronous, returning a `202 Accepted` perhaps with a `Location` header that indicates the URL
to check back at. See more in the [REST Cookbook](http://restcookbook.com/Resources/asynchroneous-operations/).

Keeping the HTTP RESTful allows us to take full advantage of all that HTTP has to offer including caching,
the ability to operate through stateless proxies and so on.

Here's an example of a `201 Created` response in which the enrollment process was completed synchronously:
```
HTTP/1.1 201 Created
Date: Fri, 14 Dec 2018 17:02:55 GMT
Server: WSGIServer/0.2 CPython/3.6.6
Content-Type: application/vnd.api+json
Location: http://127.0.0.1:8000/v1/registrations/001b55e0-9a60-4386-98c7-4c856bb840b4/
Vary: Accept
Allow: GET, POST, HEAD, OPTIONS
X-Frame-Options: SAMEORIGIN
Content-Length: 556
```
```json
{
    "data": {
        "type": "registrations",
		"id": "001b55e0-9a60-4386-98c7-4c856bb840b4",
        "attributes": {
            "uni": "abc1234",
            "enrollment": "confirmed"
        },
        "relationships": {
            "courses": {
                "data": {
                    "type": "courses",
                    "id": "01ca197f-c00c-4f24-a743-091b62f1d500"
                }
            }
        },
        "links": {
            "self": "http://127.0.0.1:8000/v1/registrations/001b55e0-9a60-4386-98c7-4c856bb840b4/"
        }
    }
}
```

An asynchronous 202 response might have shown `"enrollment": "pending"`. One would check back at the URL
shown in the `Location` header (perhaps after waiting based on a `Retry-After` header).
The newly-created resource URL is further represented in the `self` link in the JSON-formatted response body.
This particular JSON example is  styled using a format called [{json:api}](https://jsonapi.org), which
we'll delve into next.


