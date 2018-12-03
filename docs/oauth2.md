## More About Using OAuth 2.0

Review the [CU-STD-INTR-001: OAuth 2.0 Scope
Standard](https://docs.google.com/document/d/13XW4-L_j9CCeB6jAPjPHK6V5-rMpcBUiF90RIAK0f6Y/edit#heading=h.tlbkpm4wjg60):

![alt-text](./media/image2.png "OAuth 2.0 flows diagram")


### Tokens

*Access Tokens* are used for all authorization decisions. How they get
created and constrained is described below. Additional token types
include Refresh and ID tokens.

### Scopes

Scopes are *requested* by a registered Client app. They are *granted*
(and possibly *down-scoped* for so-called Enterprise Scopes) by the
OAuth 2.0 Authorization Server (AS). Scopes are then validated by the
Resource Server based on the `access_token` provided in the Authorization
Bearer header of the HTTP request. The set of scopes "in" the
access_token must match the scopes *required* by the Resource Server.
Beyond the required scopes, additional scopes might be useful for
optional capabilities.

Our implementation of scopes includes several flavors:

#### Authentication Selector Scopes

Authentication selector scopes specify what method of user
authentication the client app is requesting the AS to use. The two we
are concerned with are:

**auth-columbia**: Perform a CAS user login. See 
[Client is operating with an end user present](#client-is-operating-with-an-end-user-present),
below.

**auth-none**: Do not perform a user login. See 
[Client is a trusted server](#client-is-a-trusted-server), below.

### Scope for Client to Learn the User's Identity

In normal OAuth 2.0 operations, there may be no need for the client app
to know who the end user is. If the client does need to know this, then
use the **openid** scope. This results in an
[id_token](http://openid.net/specs/openid-connect-core-1_0.html#IDToken)
being returned to the requesting client, in addition to the usual
*access_token* -- only if the client app has been
[registered](#_c6p5zshh92vf) with permission to request
the openid scope. id_tokens only return the "sub" claim
([uni@columbia.edu](mailto:uni@columbia.edu)) unless
additional scopes are added:

**openid**: Return an id_token to the Client app.

**profile:** Added to openid, includes user's name, etc.

**email:** Added to openid, includes user's email address

There's a complementary
[userinfo](http://openid.net/specs/openid-connect-core-1_0.html#UserInfo)
endpoint that returns similar information. It is authorized using the
access_token.

TODO: Update documentation for group claim.

#### End-user Generic Scopes

A series of generic scopes are generally used for end-user data. If
requested, these scopes are **always** granted if requested, so they are
not appropriate to limit access to enterprise-owned data that the
end-user might need special permissions for 
(see [Enterprise Scopes](#enterprise-scopes)):

**create**: Permission to create new resources (POST)

**read**: Permission to read an existing resource (GET)

**update:** Permission to update an existing resource (PATCH)

**delete**: Permission to delete a resource (DELETE)

#### Enterprise Scopes

Enterprise scopes confirm (in near real-time) end-user membership in a
Grouper-managed 
"[OAUTH Group](https://docs.google.com/document/d/13XW4-L_j9CCeB6jAPjPHK6V5-rMpcBUiF90RIAK0f6Y/edit#heading=h.rn3atn9b4l3y)"
and are only applicable when combined with **auth-columbia** scope.
There are currently no real enterprise scopes defined. There is one
named **demo-netphone-admin** for demonstration purposes. Also,
**auth-columbia** is both a scope selector and an enterprise scope; one
can be effectively blocked from access via Grouper removing a user's
membership from the **auth-columbia** OAUTH Group.

Enterprise Scopes may also be used with **auth-none** scope as a means
of defining access for [trusted servers](#client-is-a-trusted-server).
In this case, both the trusted server's client credentials must be
configured to allow auth-none and the enterprise scope, for example,
sas-coursemgt-create.

### Determine Resource Server Authentication Requirements

#### Client is operating with an end user present

This use case is similar to the typical front-end client app connecting
to a back-end resource server in which the user must log in (via a
browser redirect to Shibboleth/CAS/Duo). The result is, as above, an
access token. In a fully browser-based client, the access token would be
persisted in a cookie, analogously to the way a session cookie is used.

#### Caching end-user approval

What OAuth 2.0 adds is the ability for a user to delegate permission
once to your "third party" app. In this use case, the client app
(running with it's own backend server) can persist a *Refresh Token*
which it can use to get a series of new access tokens to perform some
offline activity with the user's data. This case is powerful but not
likely to be one we use -- at least initially. Refresh Tokens are only
available with the Authorization Code grant type.

#### Client is a trusted server

This use case is the example of backend server-to-server trust that
would traditionally use IP addresses or HTTP Basic Auth to determine
whether one server should trust another. In the OAuth 2.0 world, this is
implemented by the client using HTTP Basic Auth with the AS to get back
an Access Token. Validation of (introspecting) the access token
(Authorization: "Bearer *<token>*" header) is done by the server using
HTTP Basic Auth to identify itself and then introspecting the token. No
user identity or permissions are provided because there is no user. In
addition to using the scopes associated with the access token, the
server app can always keep a list of client IDs if necessary. However,
the cleanest design approach is to base the authorization decision
entirely on the access token's scopes.

### Determine Resource Server Authorization Requirements

In all use cases, the resource server is presented with an access token
in the Authorization header. The resource server decides what actions
are authorized based on the scopes associated with the token, which it
learns from token introspection. It can also make decisions based on the
identity of the user, in the cases where a user was identified
(Authorization Code or Implicit grants) as this is exposed by the
introspection.

Resource server designers need to decide:

1.  Is a user approval required vs. a trusted server.
2.  On a per-REST method and resource basis, what scopes are required to
    implement the action (coarse-grained authorization).
3.  What additional security decisions need to be made based on the
    logged-in user and/or data (fine-grained authorization).

One should attempt to be "RESTful" in designing application security:
Base permissions on HTTP methods and resources. Using a modeling
language like OAS 3.0 can help. See
[Documenting the API in OAS 3.0](#documenting-the-api-in-oas-3.0), and the
equivalent Django
[permission_classes](#authentication-and-authorization-permission),
above.

### Register Resource Server for Token Introspection

The Resource Server must be a registered client with the OAuth 2.0
Authorization Server before it is allowed to perform token
introspection.

This process is currently manual via a service request to the IAM team.
You need to provide:

-   the name of your Resource Server (e.g. cas-coursemgt-server)
-   that it should be allowed to perform introspection (is a resource
    server)

You'll be given a *client_id* and *client_secret*. Configure these in
[settings.OAUTH2_PROVIDER](#edit-settings-to-add-drf-dja-oauth-debug-etc)
using environment variables or some other method to protect the credentials (e.g. not in the source code!).

### Register Client App(s)

Every client app must be a registered OAuth 2.0 client. Things to think
about when registering a client are:

#### Client is operating on behalf of an end user

1.  Is it a fully in-browser (javascript) app? If so, it will be using
    the Implicit grant type and will be requiring a user to log in,
    using the auth-columbia scope selector.
2.  What scopes should the app be allowed to request on behalf of the
    user and what scopes are required by its Resource Server?
3.  Should the end-user scope-approval page be presented or bypassed? In
    most cases, this will be bypassed.

#### Client is a server

In this case, the app should be registered with permission to request
the auth-none and additional scopes.
