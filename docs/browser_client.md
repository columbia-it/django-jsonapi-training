# Browser Client

The `frontend/oas-angular-app` project is a small Angular browser client for this
Django REST Framework JSON:API service. It demonstrates authenticated collection
and detail views for courses, instructors, and people.

The implementation follows the useful separation in the CUIT `sis-frontend`
example—resource models, a datastore-like service, authentication, and view
components—without copying its Angular 11 toolchain or the unmaintained
`angular2-jsonapi` dependency.

## Architecture

The client uses:

- Angular 22 standalone components and functional providers;
- `angular-auth-oidc-client` 22 with authorization code flow and PKCE;
- a small, typed JSON:API client in `src/app/core/api`;
- server-side search, sorting, pagination, and compound-document `include`;
- session storage to restore each collection's search and page.

The JSON:API client is maintained with the application instead of generated from
the OpenAPI document. This avoids committing a large generated client whose
types model the HTTP schema but do not provide JSON:API relationship behavior.
The OpenAPI schema remains available for API documentation and non-Angular
consumers.

## Run the client

Use a Node.js release supported by Angular 22, then install and start the client:

```bash
cd frontend/oas-angular-app
npm ci
npm start
```

The development server listens at `http://localhost:4200`. Run the Django service
at `http://localhost:8000`; the API and OIDC URLs are configured in
`src/app/app.config.ts`.

The OAuth application must be a public client named `demo_djt_web_client`, use
authorization code flow, and allow `http://localhost:4200` as a redirect and
post-logout redirect URI. A browser client must not have or ship a client secret.

## Build and test

```bash
npm run build
npm test -- --watch=false
```

The protected routes use the OIDC library's partial-route guard. Its HTTP
interceptor adds the bearer token only to the configured backend `/v1/` URL.

## Resource layer

`JsonApiClient` owns JSON:API request details such as bracketed pagination
parameters. `ResourceStore` selects the resource and compound-document includes.
Components depend on that layer, rather than constructing API URLs themselves.

When a backend attribute or relationship changes, update the interfaces in
`src/app/core/api/models.ts` and the relevant include path in
`src/app/core/api/resources.ts`. There is no generated source tree to refresh.

The finished client is [in this repository:material-open-in-new:]({{ view_uri }}/frontend/oas-angular-app){:target="_blank"}.
