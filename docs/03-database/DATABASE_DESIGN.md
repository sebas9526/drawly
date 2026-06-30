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
| address | TEXT |
| city | VARCHAR(80) |
| notes | TEXT |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |
| deleted_at | TIMESTAMP NULL |

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
| sold_at | TIMESTAMP NULL |
| winner_at | TIMESTAMP NULL |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |
| deleted_at | TIMESTAMP NULL |

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