# Authentication

Authentication is now implemented. Drawly is a multi-tenant SaaS: every user
(organizer) signs in and only ever sees their own raffles, tickets and
participants.

## Overview

- **Password hashing:** Argon2 (`argon2-cffi`). Passwords are never stored in
  plain text; only the Argon2 hash is persisted in `users.password_hash`.
- **Session token:** a signed JWT (HS256, `PyJWT`) whose `sub` claim is the
  user id.
- **Transport:** the JWT is delivered in an **httpOnly cookie** (`drawly_access`),
  not in a JS-readable store. This protects the token from XSS. The cookie is
  `SameSite=Lax`; set `AUTH_COOKIE_SECURE=true` behind HTTPS in production.
- **Cross-origin:** the web app sends `credentials: 'include'` so the cookie
  travels with API requests when web and API run on different origins/ports.

For backwards compatibility the API also accepts `Authorization: Bearer <token>`
if the cookie is absent (useful for scripts and future mobile clients).

## Flow

```
Register / Login  ──▶  API validates + sets httpOnly cookie (drawly_access)
        │
        ▼
Browser stores cookie (not accessible to JS)
        │
        ▼
Every request ──▶ get_current_user reads the cookie ──▶ resolves the User
        │                                   │
        │                                   └─▶ missing/invalid ⇒ 401
        ▼
Owner-scoped use cases ⇒ only the caller's data is returned
```

## Endpoints

Base path: `/api/v1/auth`.

| Method | Path        | Auth        | Description                                   |
| ------ | ----------- | ----------- | --------------------------------------------- |
| POST   | `/register` | Public      | Create an account; sets the session cookie.   |
| POST   | `/login`    | Public      | Verify credentials; sets the session cookie.  |
| POST   | `/logout`   | Public      | Clears the session cookie.                    |
| GET    | `/me`       | Cookie/JWT  | Returns the authenticated user.               |

All responses use the standard envelope (`success`, `message`, `data`). The
password hash is never serialized in any response.

### Register / Login request

```json
{ "full_name": "María Pérez", "email": "maria@example.com", "password": "at-least-8-chars" }
```

`login` omits `full_name`. Errors: `409` (email already registered on register),
`401` (invalid credentials on login).

## Route protection & data isolation

Every private router (`/raffles`, `/tickets`, `/participants`, `/dashboard`)
depends on `get_current_user`; an unauthenticated request returns `401`.

Ownership is enforced in the **backend**, never trusted from the client:

- `users` owns `raffles`, `participants` and `tickets` via a nullable
  `owner_id` FK (denormalized onto tickets so ticket queries stay owner-scoped
  without a join).
- Admin use cases are constructed with the caller's `owner_id`; every read and
  mutation is filtered by it. Fetching another user's resource by id returns
  `404` (existence is not leaked).
- The public reservation portal stays unauthenticated, but a participant created
  through it is filed under the **raffle owner**, and generated tickets inherit
  the raffle's `owner_id`.

## Configuration

Environment variables (see `apps/api/app/core/config.py`):

| Variable              | Default                | Notes                                  |
| --------------------- | ---------------------- | -------------------------------------- |
| `JWT_SECRET`          | dev-only placeholder   | **Must** be overridden in production.  |
| `JWT_ALGORITHM`       | `HS256`                |                                        |
| `JWT_EXPIRES_MINUTES` | `10080` (7 days)       | Session lifetime.                      |
| `AUTH_COOKIE_NAME`    | `drawly_access`        |                                        |
| `AUTH_COOKIE_SECURE`  | `false`                | Set `true` behind HTTPS.               |
| `AUTH_COOKIE_SAMESITE`| `lax`                  | `lax` \| `strict` \| `none`.           |

## Not yet included

Password recovery (`/forgot-password`, `/reset-password`), email verification,
social login, and roles/permissions (Owner, Administrator, Seller, Viewer)
remain future work. The `email_verified_at` column already exists for the
verification flow.
