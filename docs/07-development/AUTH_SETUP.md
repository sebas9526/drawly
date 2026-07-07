# Auth & Multi-tenancy — Setup / Upgrade Guide

What you need to install, create, and run to bring the auth + per-user data
isolation sprint online.

## 1. New backend dependencies

Added to `apps/api/pyproject.toml`:

- `argon2-cffi>=23.1,<24` — password hashing.
- `pyjwt>=2.10,<3` — signing/verifying the session JWT.

The API `Dockerfile` runs a non-frozen `uv sync`, so a plain rebuild installs
them:

```bash
docker compose build api
# or, locally, inside apps/api:
uv sync
```

(If you keep a committed `uv.lock`, run `uv lock` once on a machine with Python
3.12 to pin the two new packages.)

No new frontend npm packages — the web app reuses existing libraries
(react-hook-form, zod, TanStack Query, lucide-react, `@drawly/ui`).

## 2. New database objects — run the migration

Migration `0004_users_and_ownership` creates the `users` table and adds a
nullable, indexed `owner_id` FK to `raffles`, `participants` and `tickets`.

```bash
docker compose exec api uv run alembic upgrade head
```

It is additive and safe on an existing DB: `owner_id` is nullable, so old rows
stay valid. New rows always carry an owner.

## 3. Environment variables

Set these on the API (see `apps/api/app/core/config.py`):

| Variable              | Required?          | Notes                                   |
| --------------------- | ------------------ | --------------------------------------- |
| `JWT_SECRET`          | **Yes in prod**    | Long random string (≥ 32 bytes).        |
| `AUTH_COOKIE_SECURE`  | Prod (HTTPS)       | `true` behind HTTPS.                    |
| `AUTH_COOKIE_SAMESITE`| Optional           | `lax` (default) / `strict` / `none`.    |
| `JWT_EXPIRES_MINUTES` | Optional           | Session lifetime (default 7 days).      |
| `BACKEND_CORS_ORIGINS`| Yes                | Must list the web origin exactly (not `*`) — cookies require credentialed CORS, already enabled. |

Web app:

| Variable             | Notes                                             |
| -------------------- | ------------------------------------------------- |
| `NEXT_PUBLIC_API_URL`| API origin, e.g. `http://localhost:8000`.         |

## 4. Rebuild & run

```bash
docker compose up --build
docker compose exec api uv run alembic upgrade head   # if not auto-applied
```

Then:

1. Open the web app → you land on the **public landing page** (`/`).
2. Go to **Crear cuenta** (`/register`) → you're signed in and redirected to
   `/dashboard`.
3. The dashboard, raffles, tickets and participants now show **only your data**.
   Signing in as a different user shows a completely separate set.

## 5. What is NOT included yet

Password recovery (`/forgot-password`, `/reset-password`), email verification,
social login, and roles/permissions. `users.email_verified_at` already exists
for the future verification flow.
