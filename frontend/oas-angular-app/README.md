# Django JSON:API training client

This Angular 22 application is the browser client for the repository's Django
REST Framework JSON:API example. It provides OIDC-protected course, instructor,
and person list/detail views.

## Local development

Run the Django backend at `http://localhost:8000`, then:

```bash
npm ci
npm start
```

Open `http://localhost:4200`. The API base URL, OIDC authority, client ID, and
scopes live in `src/app/app.config.ts`.

## Verification

```bash
npm run build
npm test -- --watch=false
```

See `../../docs/browser_client.md` for the architecture, authentication setup,
and resource-layer conventions.
