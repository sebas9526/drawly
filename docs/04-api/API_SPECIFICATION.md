# API Specification

# Drawly REST API

Version: v1

Base URL

/api/v1

---

# Authentication

Cookie-based JWT (Argon2 password hashing). See `AUTHENTICATION.md` for the full
flow. All private endpoints below (raffles, tickets, participants, dashboard)
require an authenticated session and return only the caller's own data.

## Register

POST /api/v1/auth/register

Request

```json
{ "full_name": "María Pérez", "email": "maria@example.com", "password": "at-least-8-chars" }
```

Response `201 Created` — sets the `drawly_access` httpOnly cookie.

```json
{ "success": true, "message": "Account created.", "data": { "id": "…", "full_name": "María Pérez", "email": "maria@example.com", "avatar_url": null, "email_verified_at": null, "created_at": "…" } }
```

Errors: `409` email already registered.

## Login

POST /api/v1/auth/login

```json
{ "email": "maria@example.com", "password": "at-least-8-chars" }
```

Response `200 OK` — sets the session cookie. Errors: `401` invalid credentials.

## Logout

POST /api/v1/auth/logout — clears the session cookie. `200 OK`.

## Current user

GET /api/v1/auth/me — returns the authenticated user. `401` when not signed in.

---

# Collaborators

Sales collaborators per raffle (require auth; owner-scoped — a user only sees
their own collaborators). See the collaborators module in apps/api.

| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/api/v1/collaborators` | Paginated list. Filters: `search`, `raffle_id`, `is_active`; `sort` (`created_at`\|`name`\|`is_active`), `order` (`asc`\|`desc`). |
| GET | `/api/v1/collaborators/{id}` | Single collaborator. |
| POST | `/api/v1/collaborators` | Create. Body: `raffle_id`, `name`, optional `phone`, `email`, `color` (hex), `notes`, `is_active`. The raffle must belong to the caller (else 404). |
| PUT | `/api/v1/collaborators/{id}` | Update (all fields optional; `raffle_id` is fixed). |
| PATCH | `/api/v1/collaborators/{id}/activate` | Set active. |
| PATCH | `/api/v1/collaborators/{id}/deactivate` | Set inactive. |
| DELETE | `/api/v1/collaborators/{id}` | Soft delete. |
| GET | `/api/v1/collaborators/raffle/{raffle_id}` | Collaborators of a raffle (`active_only` optional). |
| GET | `/api/v1/collaborators/raffle/{raffle_id}/stats` | Per-collaborator sales: `reserved` (pending), `paid`, `total`, `total_value`. |

## Ticket ↔ collaborator

- `PATCH /api/v1/tickets/{id}/reserve` accepts an optional `collaborator_id`
  (credits the seller). `PATCH /api/v1/tickets/{id}/collaborator` reassigns or
  clears it on a reserved ticket. Both validate the collaborator belongs to the
  ticket's raffle and owner.
- Public: `GET /api/v1/public/raffles/{slug}/collaborators` lists the active
  collaborators of a published raffle, and `POST .../reserve` accepts an optional
  `collaborator_id`.

---

# Health

## Health Check

GET /health

Response

200 OK

{
  "success": true,
  "message": "API is running."
}

---

# Raffles

## Get All Raffles

GET /raffles

Query Params

page

page_size

search

status

sort

---

## Get Raffle

GET /raffles/{id}

---

## Create Raffle

POST /raffles

Request

{
  "title": "",
  "description": "",
  "prize": "",
  "ticket_price": 10000,
  "total_tickets": 100,
  "starting_number": 1,
  "draw_date": "2026-08-01T19:00:00",
  "publish_at": "2026-08-01T00:00:00"
}

`starting_number` is `0` or `1` (default `1`) — the first ticket number that
will be generated. `1` produces `"1".."total_tickets"`; `0` produces
`"0"..(total_tickets - 1)` (e.g. a 100-ticket raffle becomes `"00".."99"`
instead of `"001".."100"` once display-padded). **Immutable once set** — it is
not present on `UpdateRaffleRequest` at all, so it can never change after
creation, the same rule as `total_tickets` once tickets exist.

`publish_at` is optional (default `null`). When omitted/`null`, the raffle
publishes only via an explicit `PATCH /raffles/{id}/publish`, same as today.
When set, an in-process periodic sweep publishes the raffle automatically
once that moment passes — still subject to the same 409-if-no-tickets rule
as a manual publish; if the schedule arrives before tickets exist, the sweep
leaves the raffle in `draft` and retries on its next pass.

---

## Update Raffle

PUT /raffles/{id}

Only allowed while the raffle is in `draft`. `starting_number` is not an
accepted field — sending it returns 422 (the schema forbids unknown fields).
`publish_at` can be set or changed (same semantics as on create); there is
currently no way to explicitly clear it back to `null` via this endpoint.

---

## Generate Tickets (Sprint 3)

POST /raffles/{id}/tickets

Explicitly generates the raffle's configured `total_tickets` sequential tickets
starting from `starting_number` (status `available`). Separate from raffle
creation by design so numbering can be reconfigured before publishing. Fails
with 409 if tickets already exist, or if the raffle is not in `draft`.

Response

{
  "raffle_id": "",
  "generated": 100
}

---

## Delete Raffle

DELETE /raffles/{id}

Soft Delete

---

## Publish Raffle

PATCH /raffles/{id}/publish

---

## Publish Raffle

PATCH /raffles/{id}/publish

`draft → published`. Requires generated tickets (409 otherwise). Makes the raffle
visible on the public portal.

---

## Close Raffle

PATCH /raffles/{id}/close

---

## Select Winner

POST /raffles/{id}/winner

Response

{
    "ticket": 57,
    "participant": {},
    "winner_date": ""
}

---

# Public Portal

Unauthenticated endpoints for end users. Separate surface from the admin API —
they never expose internal ids, participant data, or admin fields. Only
`published` raffles are visible (anything else is 404).

## Get Public Raffle

GET /public/raffles/{slug}

Response data (no internal id / organization / status):

{
  "public_slug": "",
  "title": "",
  "description": "",
  "prize": "",
  "cover_image": null,
  "ticket_price": 5000,
  "draw_date": "",
  "total_tickets": 100,
  "starting_number": 1,
  "available_count": 90,
  "reserved_count": 8,
  "paid_count": 2
}

---

## List Public Tickets

GET /public/raffles/{slug}/tickets

Returns only `{ "number", "status" }` per ticket — no participant, no id.

---

## Reserve Ticket

POST /public/raffles/{slug}/reserve

Request

{
  "ticket_number": 57,
  "participant": {
    "full_name": "",
    "phone": "",
    "email": "",
    "document": ""
  }
}

Reuses an existing participant by phone (no duplicates), assigns it, and reserves
the ticket. 404 if the raffle isn't published or the number doesn't exist; 409 if
the ticket is no longer available (the backend is the source of truth).

Response

{
  "ticket_number": 57,
  "raffle_title": "",
  "status": "reserved"
}

---

# Participants

A participant owns zero-or-more tickets. Phone uniqueness is enforced in the
domain among active (non-deleted) participants. Delete is a soft delete and is
blocked (409) while the participant still has tickets assigned.

## List Participants

GET /participants

Query Params

page

page_size

search  (matches name, phone, document, or email)

Paginated envelope.

---

## Get Participant

GET /participants/{id}

Includes `ticket_count`.

---

## Create Participant

POST /participants

Request

{
  "full_name": "",
  "phone": "",
  "email": "",
  "document": "",
  "address": "",
  "city": "",
  "notes": ""
}

`full_name` and `phone` are required. 409 if the phone already exists.

---

## Update Participant

PATCH /participants/{id}

Partial update. 409 if a changed phone collides with another participant.

---

## Delete Participant

DELETE /participants/{id}

Soft delete. 409 if the participant still has tickets assigned.

---

## Participant Tickets

GET /participants/{id}/tickets

Returns the participant's tickets (ticket read models, no payments).

---

# Tickets

Ticket lifecycle: `available → reserved → paid`, with `reserved → available`
(cancel) and `winner` reserved for the future draw. Every transition is enforced
server-side by the tickets domain service; a `paid` ticket is immutable.

## List Tickets

GET /tickets

Query Params

page

page_size

raffle_id

status

Paginated envelope.

---

## List Available Tickets

GET /tickets/available?raffle_id={id}

Returns only `available` tickets for a raffle.

---

## Ticket Detail

GET /tickets/{id}

---

## Reserve Ticket

PATCH /tickets/{id}/reserve

Request (optional)

{
  "participant_id": ""
}

`available → reserved`. Sets `reserved_at` and `expires_at`. 409 if not available.

---

## Cancel Reservation

PATCH /tickets/{id}/cancel

`reserved → available`. Clears the participant link, `reserved_at`, `expires_at`.

---

## Mark Ticket as Paid

PATCH /tickets/{id}/pay

`reserved → paid`. Sets `sold_at`. 409 if the ticket is not reserved.

---

## Assign / Change Participant

PATCH /tickets/{id}/participant

Request

{
  "participant_id": ""
}

Assigns or changes the ticket's participant. An `available` ticket is reserved
for the participant; a `reserved` ticket has its participant changed. 409 on a
paid/winner ticket, 404 if the participant does not exist.

---

## Remove Participant

DELETE /tickets/{id}/participant

Removes the participant from a reserved ticket, releasing it back to `available`
(clears `reserved_at` / `expires_at`). 409 on a paid ticket.

---

# Dashboard

Admin-only reporting. Prefer the single aggregated `overview` endpoint (one
request builds the whole dashboard). Backed by a read model with grouped
aggregate queries — no per-metric COUNT(*) round-trips.

## Overview

GET /dashboard/overview

Response data:

{
  "raffles":  { "total", "active", "draft", "published", "closed", "archived" },
  "tickets":  { "total", "available", "reserved", "paid" },
  "participants": 0,
  "sales":    { "potential_value", "reserved_value", "paid_value" },
  "recent_reservations": [
    { "number", "raffle_title", "participant_name", "reserved_at" }
  ],
  "recent_raffles": [
    { "title", "status", "total_tickets", "available_count" }
  ]
}

`sales` are derived/potential values (`ticket_price` × counts) — there are no
real payments yet. `active` = draft + published.

## Recent Reservations

GET /dashboard/reservations

Latest reservations (same items as `overview.recent_reservations`).

## Recent Raffles

GET /dashboard/raffles

Latest raffles (same items as `overview.recent_raffles`).

---

# Analytics (Sprint 9)

Independent read-model module (`modules/analytics`) — it does not import
`modules/dashboard`; the two evolve separately. Every endpoint is owner-scoped
and never returns another user's data. All aggregation happens in SQL
(grouped/aggregated statements); the frontend never recomputes stats.

Shared query filters (all optional, applied per-endpoint — see each section):

- `start_date`, `end_date` (`YYYY-MM-DD`) — bound `Ticket.reserved_at` (every
  reserved/paid/winner ticket has it set); `sales_by_day` alone buckets by
  `Ticket.sold_at` instead, since it reports sales *by day sold*.
- `raffle_id` — scope to one raffle.
- `status` — a **ticket** status (`available|reserved|paid`). Not applied to
  the raffles report (see `raffle_status` below) nor to the collaborator/
  participant reports, which already break results out by ticket status.
- `collaborator_id` — scope to one collaborator's tickets.

## Executive Dashboard

GET /analytics/dashboard

Response data:

{
  "raffles_total", "raffles_published", "raffles_closed",
  "tickets_available", "tickets_reserved", "tickets_paid",
  "participants_total", "collaborators_total",
  "expected_revenue", "received_revenue",
  "percent_sold", "percent_reserved"
}

`expected_revenue` = `total_tickets × ticket_price` summed across matched
raffles. `received_revenue` = sum of `ticket_price` for PAID tickets — derived
from ticket status, not a real transaction; the seat reserved for the future
Payments module.

GET /analytics/dashboard/export?format=excel|pdf — same figures as a
downloadable file.

## Raffle Report

GET /analytics/raffles (paginated: `page`, `page_size`, plus `raffle_status`
instead of `status`)

Response data (per row): `{ id, title, status, created_at, draw_date,
total_tickets, available, reserved, paid, percent_sold, expected_revenue }`

GET /analytics/raffles/{raffle_id} — single-raffle detail, adds
`top_collaborators` and `top_participants` (Top-5 rankings, PAID tickets only).
Computed only for one raffle at a time (never per-row in the list) to avoid
N+1 queries.

GET /analytics/raffles/export?format=excel|pdf

## Collaborator Report

GET /analytics/collaborators

Response data (array, ranked by `expected_amount` descending): `{ id, name,
raffle_id, raffle_title, total_sales, total_reservations,
participants_served, expected_amount, participation_percent, rank }`

`participation_percent` = this collaborator's PAID tickets ÷ the raffle's
`total_tickets`. Not paginated — bounded by how many collaborators one owner
manages.

GET /analytics/collaborators/export?format=excel|pdf

## Participant Report

GET /analytics/participants

Response data (array): `{ id, full_name, purchases_count, tickets_count,
amount_invested, last_purchase_at, raffles_count }`

`purchases_count`/`amount_invested` count PAID tickets only; `tickets_count`
counts every ticket currently assigned (reserved + paid + winner). Not
paginated yet — a scalability follow-up once a single owner's participant base
grows very large.

GET /analytics/participants/export?format=excel|pdf

## Global Reports (Sales)

GET /analytics/sales

Response data:

{
  "top_collaborators": [{ "id", "name", "count", "value", "rank" }],
  "top_raffles":       [{ "id", "name", "count", "value", "rank" }],
  "top_participants":  [{ "id", "name", "count", "value", "rank" }],
  "sales_by_day":        [{ "day", "count", "value" }],
  "reservations_by_day": [{ "day", "count" }],
  "status_distribution": { "available", "reserved", "paid", "cancelled", "winner" }
}

Top-N rankings are PAID-only, Top-10, ordered by value descending.
`cancelled`/`winner` are always 0 today — those ticket-lifecycle transitions
aren't wired to any use case yet (no draw/cancellation feature exists), so the
counts are honestly zero rather than simulated.

## Exports

Every `/export` endpoint accepts `?format=excel` (real `.xlsx` via `openpyxl`)
or `?format=pdf` (real `.pdf` via `reportlab`) and streams the file with a
`Content-Disposition: attachment` header — same rows the on-screen report
shows, no separate export-only query path.

---

# Future Endpoints

/users

/auth

/payments

/notifications

/reports

/settings

/webhooks

/organizations
