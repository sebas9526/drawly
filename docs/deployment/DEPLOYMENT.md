# Deployment — Vercel + Render + Neon

Drawly deploys as three independent pieces:

| Piece | Platform | Source |
|---|---|---|
| Frontend (`@drawly/web`) | [Vercel](https://vercel.com) | `apps/web` |
| Backend (`drawly-api`) | [Render](https://render.com) | `apps/api` |
| Database | [Neon](https://neon.tech) (managed PostgreSQL) | — |

Local development (`docker compose up --build`) is unaffected by anything on
this page — it keeps using its own `postgres` container, never Neon.

---

## 1. Neon (PostgreSQL)

1. Create a Neon project (any region close to where Render will run — see
   step 2). Note the **database name** Neon gives you (default `neondb`;
   rename it or create a `drawly` database if you prefer).
2. From the Neon dashboard, **Connection Details**, copy the connection
   string. Use the **direct** connection (the one *without* `-pooler` in the
   hostname), not the pooled one — see [Neon pooling](#neon-pooling) below.
3. Build the two URLs the API needs from it. Given a Neon string like:

   ```text
   postgresql://alice:AbC123@ep-cool-forest-12345.us-east-2.aws.neon.tech/drawly?sslmode=require
   ```

   derive:

   ```bash
   # Async (used by the running app) — note the param is `ssl`, not `sslmode`.
   DATABASE_URL=postgresql+asyncpg://alice:AbC123@ep-cool-forest-12345.us-east-2.aws.neon.tech/drawly?ssl=require

   # Sync (used by Alembic migrations) — `sslmode` is correct here.
   DATABASE_URL_SYNC=postgresql+psycopg://alice:AbC123@ep-cool-forest-12345.us-east-2.aws.neon.tech/drawly?sslmode=require
   ```

   <a id="ssl-param-warning"></a>
   **This distinction is not cosmetic.** SQLAlchemy's asyncpg dialect passes
   every URL query parameter straight through as a keyword argument to
   `asyncpg.connect()`, which has an `ssl` parameter but no `sslmode`
   parameter at all — a `DATABASE_URL` with `?sslmode=require` fails at
   connection time with `TypeError: connect() got an unexpected keyword
   argument 'sslmode'`. `psycopg` (used only for `DATABASE_URL_SYNC`) follows
   libpq conventions natively, so `sslmode` is correct *there*. Verified
   against the installed driver versions (`asyncpg==0.30.0`,
   `sqlalchemy==2.0.49`) in this repo.
4. Migrations run automatically on every deploy — Render's Docker image runs
   `alembic upgrade head` before starting uvicorn (see
   `apps/api/docker-entrypoint.sh`). No manual migration step is required
   after the first deploy; only for local one-off runs:

   ```bash
   cd apps/api
   DATABASE_URL_SYNC="<your Neon sync URL>" uv run alembic upgrade head
   ```

<a id="neon-pooling"></a>
### Neon's pooled connection string (read before switching to it)

Neon offers a second, PgBouncer-pooled connection string (hostname contains
`-pooler`). Render's API service is a small number of long-lived processes
(not a serverless/edge function), so the direct connection string above is
the right default — it needs no extra configuration and every existing
connection-pool setting in the codebase (SQLAlchemy's own async engine pool)
already fits it. If Neon's direct connection limit ever becomes a problem
under load, the pooled string can be used instead, but only in **transaction
pooling** mode with `asyncpg`'s prepared-statement cache explicitly disabled
(`statement_cache_size=0` in `connect_args`) — PgBouncer transaction pooling
and asyncpg's default prepared-statement caching are incompatible and fail in
non-obvious ways otherwise. Not configured today; flagged here so it's a
deliberate future change, not a surprise.

---

## 2. Render (backend — `apps/api`)

### Option A — Blueprint (`render.yaml`, recommended)

The repo root has a `render.yaml`. In the Render dashboard: **New → Blueprint
→** select this repository. Render reads `render.yaml` and creates the
`drawly-api` service with the settings below pre-filled. You still need to
fill in the values marked `sync: false` (Neon URLs, CORS origin) from the
service's **Environment** tab after the first deploy.

### Option B — Manual dashboard configuration

**New → Web Service** → connect the repository, then:

| Setting | Value |
|---|---|
| **Runtime** | Docker |
| **Root Directory** | `apps/api` |
| **Dockerfile Path** | `Dockerfile` |
| **Docker Build Context Directory** | `.` (i.e. `apps/api`, relative to Root Directory) |
| **Build Command** | *(not used — Docker runtime builds the Dockerfile itself)* |
| **Start Command** | *(not used — the Dockerfile's `CMD` runs)* |
| **Health Check Path** | `/health` |
| **Port** | Auto-detected from the Dockerfile's `EXPOSE 8000`; no `PORT` env var needed |

The Dockerfile has four stages (`base → deps → dev → production`); `docker
build` with no `--target` builds the **last** stage, which is `production`
— Render needs no extra flag to get the right one. That stage already runs
`uv sync --no-dev` (dev-only tooling like pytest/mypy/ruff never ships) and
starts `uvicorn` with `--workers 4`.

**Environment variables** (Render dashboard → Environment, or via
`render.yaml`) — see `.env.production.example` for the full annotated list.
The ones that differ from every code default:

| Variable | Value | Why |
|---|---|---|
| `ENVIRONMENT` | `production` | |
| `DEBUG` | `false` | Disables verbose SQL echo. |
| `DATABASE_URL` | Neon async URL (`?ssl=require`) | See [Neon](#1-neon-postgresql). |
| `DATABASE_URL_SYNC` | Neon sync URL (`?sslmode=require`) | Used by Alembic. |
| `JWT_SECRET` | A long random value | `render.yaml` generates this automatically (`generateValue: true`); set by hand only if configuring manually. Never reuse the code's dev default (`dev-insecure-change-me-in-production-please-32b`) — the app doesn't refuse to boot with it, so this is a step that's easy to silently skip. |
| `BACKEND_CORS_ORIGINS` | `https://your-app.vercel.app` | The deployed Vercel origin, exact match (no wildcard — required because the API sets `allow_credentials=True`). |
| `AUTH_COOKIE_SECURE` | `true` | Required once traffic is HTTPS (Render always is). |
| `AUTH_COOKIE_SAMESITE` | `none` | Required because Vercel and Render are different sites — see [CORS y autenticación](#4-cors-y-autenticación-dominios-cruzados). |

Every other setting (rate limiting, reservation TTL/sweep interval, JWT
algorithm/expiry, cookie name) has a production-sane default and needs no
override — see `.env.production.example` for the full list if you want to
tune them.

---

## 3. Vercel (frontend — `apps/web`)

### The "No Next.js version detected" error

This fires when Vercel's zero-config detection inspects the **wrong**
`package.json` — almost always because the project's **Root Directory** is
still the repo root, whose `package.json` has no `next` dependency (only
`apps/web/package.json` does, since this is a pnpm workspace monorepo). Fix:

**Project Settings → General → Root Directory → `apps/web`.**

This is a dashboard-only setting; nothing in the repo can set it for you.
Once it's correct, Vercel auto-detects Next.js from `apps/web/package.json`
and the error disappears.

### Full configuration

| Setting | Value |
|---|---|
| **Root Directory** | `apps/web` — **the required fix above** |
| **Framework Preset** | Next.js (auto-detected once Root Directory is correct; also pinned explicitly in `apps/web/vercel.json`) |
| **Install Command** | `cd ../.. && pnpm install --frozen-lockfile` (from `apps/web/vercel.json`) |
| **Build Command** | `cd ../.. && pnpm turbo run build --filter=@drawly/web` (from `apps/web/vercel.json`) |
| **Output Directory** | *(default — Next.js framework preset handles this)* |

`apps/web/vercel.json` exists specifically so these commands don't need to be
retyped into the dashboard by hand. It's only read once Root Directory points
at `apps/web` (Vercel resolves `vercel.json` relative to Root Directory).

The build command goes through `turbo run build` rather than a bare `next
build` so that Vercel's automatic Turborepo Remote Cache applies (Vercel
detects `turbo.json` in the monorepo and enables it with no extra
configuration) — repeat deploys where `apps/web` hasn't changed reuse the
cached build instead of rebuilding.

Every `@drawly/*` workspace package (`ui`, `utils`, `api-client`, `types`,
`constants`, `hooks`, `validators`, `config`) ships raw TypeScript source with
no build step of its own — `next.config.ts`'s `transpilePackages` list
handles compiling them as part of the Next.js build. This list was missing
`@drawly/hooks` and `@drawly/validators` (added in Sprint 10) before this
audit; both are now included.

**Environment variables** (Vercel dashboard → Settings → Environment
Variables):

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://drawly-api.onrender.com` (the Render service's URL, no trailing slash) |

Only one variable — the frontend has no other environment-dependent
configuration (confirmed by grepping every `process.env.*` reference in
`apps/web/src` and `packages/*/src`).

`NEXT_PUBLIC_*` variables are inlined into the client JavaScript bundle at
**build** time, not read at runtime — changing this value requires a new
build, and `turbo.json`'s `build.env` now declares it explicitly so
Turborepo's (and Vercel's Remote Cache's) cache key changes whenever it does,
instead of silently reusing a bundle baked for a different backend.

---

## 4. CORS y autenticación (dominios cruzados)

Vercel (`*.vercel.app` or a custom domain) and Render (`*.onrender.com` or a
custom domain) are **different sites** from the browser's perspective — this
is a genuinely cross-site deployment, not just cross-port like local dev.
Three settings have to agree for the session cookie to survive:

1. **CORS** (`BACKEND_CORS_ORIGINS`) — must be the exact Vercel origin, not
   `*`. FastAPI's `CORSMiddleware` is already configured with
   `allow_credentials=True`, which browsers refuse to honor together with a
   wildcard origin — an exact origin is required either way.
2. **Cookie `SameSite`** (`AUTH_COOKIE_SAMESITE=none`) — the code default is
   `lax` (correct for local dev, where frontend and API are both
   `localhost`). `Lax` cookies are *not* sent on cross-site `fetch()`/XHR
   calls (only on top-level navigation) — every API call this SPA makes is
   exactly the kind of request `Lax` blocks. Must be `none` in production.
3. **Cookie `Secure`** (`AUTH_COOKIE_SECURE=true`) — browsers reject
   `SameSite=None` cookies that aren't also `Secure`. Both Vercel and Render
   serve over HTTPS by default, so this is safe to always enable in
   production.

The frontend side needed no changes: `packages/api-client`'s fetch wrapper
already sends `credentials: 'include'` on every request by default (see
`packages/api-client/src/client/http.ts`), and the JWT is never read from or
written to `localStorage` — it only ever exists in the httpOnly cookie the
API sets, which JavaScript can't touch either way. Verified via
`.env.production.example`'s values; no code changes were required for any of
the three settings above, since they were already environment-configurable.

---

## 5. Deployment checklist

**Neon**
- [ ] Project created; direct (non-pooler) connection string copied.
- [ ] `DATABASE_URL` built with `?ssl=require` (not `sslmode`).
- [ ] `DATABASE_URL_SYNC` built with `?sslmode=require`.

**Render**
- [ ] Service created (Blueprint via `render.yaml`, or manual — Runtime:
      Docker, Root Directory: `apps/api`).
- [ ] `DATABASE_URL` / `DATABASE_URL_SYNC` set to the Neon URLs above.
- [ ] `JWT_SECRET` set to a real random value (never the dev default).
- [ ] `BACKEND_CORS_ORIGINS` set to the exact Vercel URL (added *after* the
      Vercel deploy exists, since you need its final URL first).
- [ ] `AUTH_COOKIE_SECURE=true` and `AUTH_COOKIE_SAMESITE=none` set.
- [ ] First deploy succeeds; `/health` returns `{"success": true, ...}`.
- [ ] Render logs show `[entrypoint] Migrations applied.` on startup.

**Vercel**
- [ ] Root Directory set to `apps/web` (fixes "No Next.js version detected").
- [ ] `NEXT_PUBLIC_API_URL` set to the Render service's URL.
- [ ] Deploy succeeds; the deployed site loads `/login` and `/register`.

**Cross-service**
- [ ] After both are deployed: confirm `BACKEND_CORS_ORIGINS` on Render
      matches the *actual* Vercel URL (custom domain if you attached one —
      update it again if the domain changes later).
- [ ] From the deployed frontend: register a user, log in, refresh the page
      and confirm the session persists (proves the cross-site cookie is
      actually being accepted — this is the step most likely to silently
      fail if any of the three settings in
      [§4](#4-cors-y-autenticación-dominios-cruzados) is wrong).
- [ ] Create a raffle, generate tickets, publish, reserve one from the public
      link — exercises the full stack end to end.

---

## 6. Local development is unaffected

`docker compose up --build` continues to work exactly as before — it never
reads `.env.production.example`, `render.yaml`, or `apps/web/vercel.json`,
and `docker-compose.yml` still overrides `DATABASE_URL`/`DATABASE_URL_SYNC`
to point at its own `postgres` container regardless of what's in `.env`. See
`.env.development` for a ready-to-copy local `.env`.
