# Database Design

# Drawly Database Design

Version: 1.0

---

# Database Engine

PostgreSQL 17

---

# ORM

SQLModel

---

# Migration Tool

Alembic

---

# Naming Convention

Tables

snake_case

Example

raffles

ticket_reservations

participants

Columns

snake_case

Example

created_at

ticket_price

draw_date

Foreign Keys

<entity>_id

Example

raffle_id

participant_id

organization_id

---

# Primary Keys

Every table uses UUID.

Example

id UUID PRIMARY KEY

---

# Audit Fields

Every table contains

id

created_at

updated_at

deleted_at

deleted_at is nullable and used for Soft Delete.

---

# Tables

## users

Added in migration `0004_users_and_ownership`. A platform user (organizer) who
owns raffles, participants and tickets.

| Column | Type |
|---------|------|
| id | UUID |
| full_name | VARCHAR(150) |
| email | VARCHAR(150) UNIQUE |
| password_hash | VARCHAR(255) |
| avatar_url | TEXT NULL |
| email_verified_at | TIMESTAMP NULL |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |
| deleted_at | TIMESTAMP NULL |

- `password_hash` stores an **Argon2** hash — passwords are never stored in
  plain text.
- `email` is unique among all users (case-normalized to lowercase in the
  domain).
- `email_verified_at` is reserved for the future email-verification flow.

### Ownership (multi-tenancy)

Migration `0004` also adds a nullable `owner_id UUID` FK → `users.id` to
`raffles`, `participants` and `tickets` (each indexed). It is nullable so rows
created before auth remain valid; every new row carries an owner. `owner_id` is
denormalized onto `tickets` so ticket queries can be owner-scoped without a join
to `raffles`. All admin queries filter by `owner_id`, guaranteeing per-user data
isolation in the backend.

---

## collaborators

Added in migration `0005_collaborators`. A sales collaborator (seller) that
belongs to a single raffle. Each raffle has many collaborators; a ticket may
record which collaborator made the sale.

| Column | Type |
|---------|------|
| id | UUID |
| owner_id | UUID NULL (FK users.id) |
| raffle_id | UUID (FK raffles.id) |
| user_id | UUID NULL (FK users.id) |
| name | VARCHAR(150) |
| phone | VARCHAR(30) NULL |
| email | VARCHAR(150) NULL |
| color | VARCHAR(9) |
| notes | TEXT NULL |
| is_active | BOOLEAN |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |
| deleted_at | TIMESTAMP NULL |

- `owner_id` is denormalized from the raffle owner so admin queries stay
  owner-scoped without a join (same pattern as tickets). All collaborator
  queries filter by `owner_id`.
- `raffle_id` scopes the collaborator to one raffle; listing/stats are per-raffle.
- **`user_id` (growth path):** reserved and nullable. A collaborator is not a
  platform user today, but linking this column to `users.id` later lets a
  collaborator log in and see only their own sales — additive, no rewrite.
- `tickets.collaborator_id` (nullable FK, added in the same migration) credits
  the seller of a reserved/paid ticket. Available tickets have none. It is
  cleared when a reservation is cancelled and validated to belong to the ticket's
  raffle (and owner) before it is set.

---

## organizations

| Column | Type |
|---------|------|
| id | UUID |
| name | VARCHAR(120) |
| email | VARCHAR(150) |
| phone | VARCHAR(30) |
| logo | TEXT |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |
| deleted_at | TIMESTAMP NULL |

---

## raffles

| Column | Type |
|---------|------|
| id | UUID |
| organization_id | UUID |
| title | VARCHAR(150) |
| description | TEXT |
| prize | TEXT |
| cover_image | TEXT |
| ticket_price | NUMERIC(12,2) |
| total_tickets | INTEGER |
| draw_date | TIMESTAMP |
| status | VARCHAR(20) |
| public_slug | VARCHAR(120) UNIQUE |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |
| deleted_at | TIMESTAMP NULL |

---

## participants

| Column | Type |
|---------|------|
| id | UUID |
| full_name | VARCHAR(150) |
| phone | VARCHAR(30) |
| email | VARCHAR(150) |
| document | VARCHAR(50) |
| address | TEXT |
| city | VARCHAR(80) |
| notes | TEXT |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |
| deleted_at | TIMESTAMP NULL |

Notes (Sprint 4):

- `document` is optional and indexed (used for search).
- `phone` is NOT unique at the DB level; uniqueness is enforced in the domain
  among active (non-deleted) participants.
- `tickets.participant_id` is now a real FK to `participants.id` (added in
  migration `0002_participants`); no cascade — deletes are soft and blocked while
  tickets are assigned.

---

## tickets

| Column | Type |
|---------|------|
| id | UUID |
| raffle_id | UUID |
| participant_id | UUID NULL |
| number | INTEGER |
| status | VARCHAR(20) |
| reserved_at | TIMESTAMP NULL |
| expires_at | TIMESTAMP NULL |
| sold_at | TIMESTAMP NULL |
| winner_at | TIMESTAMP NULL |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |
| deleted_at | TIMESTAMP NULL |

Notes (Sprint 3):

- Timestamps are stored timezone-aware (`TIMESTAMPTZ`).
- `expires_at` marks reservation expiry; it is set on reserve but no background
  job releases expired reservations yet.
- `raffle_id` has a real FK to `raffles`. `participant_id` is a nullable UUID
  without a FK until the participants module exists. Likewise `raffles.organization_id`
  is nullable/no-FK until the organizations module exists.

---

# Relationships

organizations

1 ---- *

raffles

raffles

1 ---- *

tickets

participants

1 ---- *

tickets

---

# Constraints

Ticket number must be unique per raffle.

UNIQUE(raffle_id, number)

---

Slug must be unique.

UNIQUE(public_slug)

---

Phone is not unique.

Email is optional.

---

# Soft Delete

Every delete operation updates

deleted_at

instead of removing the row.

---

# Indexes

raffles

organization_id

status

draw_date

public_slug

participants

phone

email

tickets

raffle_id

participant_id

status

number

reserved_at  (Sprint 6 — backs the dashboard "recent reservations" ordering)

sold_at  (Sprint 9 — backs the analytics "sales per day" time series; also
already set on the PAID transition since Sprint 3)

Sprint 9 (Analytics & Reports) added no new tables or columns — every report
is a read model over the existing `raffles`/`tickets`/`participants`/
`collaborators` tables, aggregated in SQL (`GROUP BY`, `func.count`/`func.sum`,
correlated scalar subqueries). `received_revenue` in the analytics dashboard is
derived from `tickets.status = 'paid'`, not a real transaction — see `payments`
under Future Tables below for where that eventually lands.

---

# Future Tables

users

payments

payment_transactions

notifications

audit_logs

roles

permissions

organization_members

webhooks

settings

activity_logs

---

# Database Principles

No cascade delete.

No duplicated business data.

Every foreign key indexed.

UUID everywhere.

Soft delete by default.

Audit fields in every table.

Business integrity enforced by database constraints.