## HTTP and REpresentational State Transfer (REST)

### RESTful APIs

* ORM API using HTTP
* Client-server - separation of concerns, allows independent evolution of
components.
* Stateless - no session state maintained between requests
* Layered - Client/Server don't care if additional layers (e.g. caches,
  load balancers) are in between.
* Uniform interface:
  - Resource collections and items within collections: ID in URL
  - Use of HTTP request methods and responses as designed (contrasted with SOAP/WSDL?)
* Idempotent (hopefully) - same request can be duplicated with equivalent
  result
* Cacheable - frequently referenced data can be cached to avoid
  unnecessary network traffic. Can happen at multiple levels (client,
  cache in front of server, cached in server, etc.)

#### Avoid REST anti-patterns

It is unfortunately common to see non-RESTful patterns sneaking into RESTful APIs. The most
common of these anti-patterns is turning a REST API endpoint into a SOAP-like endpoint by invoking
a remote method call. For example, `POST /v1/courses/01ca197f-c00c-4f24-a743-091b62f1d500/register` (with
a request body containing a JSON document with other information like the identity of the registrant).
You can immediately tell this is an anti-pattern because "register" is a verb and RESTful resources
should only be nouns.

#### A good REST pattern

A RESTful approach to the above might be something along the lines of:
`POST /v1/registrations/` with a body containing:
```json
{
    "data": {
        "type": "registrations",
        "attributes": {
            "uni": "abc1234",
            "status": "pending"
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
registration process. This could be synchronous, returning a final `201 Created` status
or asynchronous, returning a `202 Accepted` perhaps with a `Location` header indicate the URL
to check back at. See more in the [REST Cookbook](http://restcookbook.com/Resources/asynchroneous-operations/).

Keeping the HTTP RESTful allows us to take full advantage of all that HTTP has to offer including caching,
the ability to operate through stateless proxies and so on.

### HTTP Requests

Consists of a verb (HTTP method), scheme (http/https), server, port and
noun (resource), and query parameters.

e.g. GET `https://example.com:8000/api/widgets/123?sort=-name`


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


#### HATEOAS: Hypermedia As The Engine Of Application State.

Given a starting URL, client app *should* be able to navigate everything
without any separate external documentation of the interface.

#### Request Body

Usually where longer form parameters or content is POSTed. Content-type
header specifies what kind of content is being POSTed, PATCHed or PUT.
For our purposes this will be `application/json` or a variant such as `application/vnd.api+json`.

#### Response Body

The response to the request. Can be empty (204 No Content).
The response's _Content-type_ header specifies which of
the (possible list of) request's _Accept_ header content types is provided. 

#### Query Parameters

Usually short parameters to modify a request

Example: `GET /api/v1/widgets?sort=-name,+qty`

#### Headers

The HTTP Accepts header lists what (prioritized) content types the
requestor will accept: `Accept: application/json`

The HTTP Content-Type header specifies the format of the response:
`Content-type: application/json`

#### Authentication and Authorization

The HTTP Authorization header is commonly used for access control. There
are 3 main styles:

1.  **Authorization: Bearer *token*** header -- used with OAuth 2 and
    REST APIs. Stateless.

2.  **Authorization: Basic *b64-encoded-user:password*** header --
    Common for server-to-server, including REST. Stateless.

3.  **Session** -- Used by conventional browser-based apps with a user
    at one end. Maintains state across multiple HTTP request/response
    iterations via session cookies (`Set-Cookie` response and `Cookie` request headers)

Our "real" apps will use Bearer tokens. For testing in Django, it can be
more convenient to use Basic auth as Bearer tokens have to be refreshed
from time-to-time. We'll see how to configure these below.
