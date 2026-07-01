# @drawly/api-client

Framework-agnostic HTTP client for the Drawly API. Uses native `fetch`, has no
React/Next.js dependency, and is safe to reuse from a future React Native app.

## Usage

```ts
import { createDrawlyApiClient } from '@drawly/api-client';

const api = createDrawlyApiClient({
  baseUrl: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
  getToken: () => localStorage.getItem('drawly.access_token'),
  onUnauthorized: () => {
    /* e.g. redirect to login */
  },
});

const { status } = await api.health.check();
const { data: raffles, pagination } = await api.raffles.list({ page: 1 });
```

## Layout

- `client/` — the low-level plumbing (`ApiClient`, fetch wrapper, auth
  interceptor, envelope parsing, error types). No endpoint knows about any of
  this beyond calling `client.get/post/put/patch/delete/getPaginated`.
- `endpoints/` — one factory function per domain (`createRafflesEndpoints`,
  etc.), each just a set of typed, thin HTTP calls. No business rules live
  here — validation and domain logic belong to the backend and to each
  feature module, not to this package.
- `dto/` — wire-format types (deliberately `snake_case`, mirroring the JSON
  the API actually sends) for request/response bodies.
- `types/` — client-internal types not tied to a specific domain.
- `utils/` — HTTP-specific helpers (e.g. query-string building).

`auth.ts` and `organizations.ts` are marked provisional in code — the backend
doesn't implement those routes yet (see `docs/04-api/AUTHENTICATION.md` and
the "Future Endpoints" section of `docs/04-api/API_SPECIFICATION.md`).
