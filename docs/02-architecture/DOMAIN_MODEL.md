# Domain Model

# Drawly Domain Model

Version: 1.0

---

# Purpose

This document defines the business domain of Drawly.

It establishes the core entities, their relationships, business rules, and lifecycle.

This document is the single source of truth for the backend, frontend, and database.

---

# Domain Overview

The Drawly domain revolves around the creation and management of numbered raffles.

The primary business flow is:

Organization
    ↓
Raffle
    ↓
Tickets
    ↓
Participants
    ↓
Winner

---

# Core Entities

## Organization

Represents the owner of one or more raffles.

Although the MVP only supports a single organization, the architecture must be multi-tenant ready.

### Attributes

- id
- name
- email
- phone
- logo
- createdAt
- updatedAt

### Relationships

Organization

→ has many Raffles

---

## Raffle

Represents a raffle created by an organizer.

### Attributes

- id
- title
- description
- prize
- coverImage
- ticketPrice
- totalTickets
- startingNumber
- drawDate
- status
- publicSlug
- createdAt
- updatedAt

> `startingNumber` (`0` or `1`, default `1`) fixes the first ticket number
> generated, so a 100-ticket raffle can produce `"00".."99"` instead of the
> default `"001".."100"`. Set at creation only — immutable afterwards, same
> rule as `totalTickets` once tickets exist.

### Relationships

Raffle

→ belongs to Organization

→ has many Tickets

---

## Ticket

Represents a numbered ticket inside a raffle.

### Attributes

- id
- number
- status
- reservedAt
- expiresAt
- soldAt
- winnerAt

> Ticket generation is an **explicit action** (`POST /raffles/{id}/tickets`),
> intentionally decoupled from raffle creation so the numbering/format can be
> reconfigured before publishing. `expiresAt` records reservation expiry (set on
> reserve); automatic release of expired reservations is future work.
> `number` starts at the raffle's `startingNumber` (`0` or `1`), so it may be
> `0` for a raffle configured to start at zero.

### Relationships

Ticket

→ belongs to Raffle

→ optionally belongs to Participant

---

## Participant

Represents the customer buying one or multiple tickets.

### Attributes

- id
- fullName
- phone
- email
- document
- address
- city
- notes
- createdAt

### Relationships

Participant

→ owns many Tickets (a ticket has zero or one participant)

### Business Rules (Sprint 4)

- Name and phone are required; phone is unique among active participants.
- Delete is a soft delete and is blocked while the participant has tickets.
- Assigning a participant to an available ticket reserves it; removing the
  participant from a reserved ticket releases it back to available.

> **Future — Customer:** this entity is intentionally shaped to grow into a
> `Customer` (one customer across many raffles over time), where "participation"
> becomes the customer↔ticket link. Tickets already reference the participant, so
> the evolution is additive rather than a rewrite. The MVP keeps the name
> `Participant`.

---

## Collaborator (Sprint 7)

A sales collaborator (seller) that belongs to a single raffle. A raffle has many
collaborators; a collaborator belongs to exactly one raffle.

### Attributes

- name (required), phone, email, color, notes, is_active
- owner_id (the organizer; denormalized for tenant scoping)
- raffle_id (the raffle it belongs to)
- user_id (**reserved, nullable** — future login link)

### Relationships

- Raffle 1—N Collaborator.
- Collaborator 0—N Ticket (via `tickets.collaborator_id`, nullable): a reserved
  or paid ticket may credit the collaborator who sold it. Available tickets have
  none.

### Business Rules (Sprint 7)

- A collaborator can only be created on a raffle the caller owns.
- Everything is owner-scoped: a user never sees another user's collaborators,
  and a ticket can only be credited to a collaborator of its own raffle/owner.
- Crediting a collaborator is optional (both admin and public reservation).
- Delete is a soft delete; tickets already sold keep the historical credit.

> **Future — Collaborator as User:** the `user_id` column is reserved so a
> collaborator can later be linked to a platform `User` and log in to see only
> their own sales:
> `User (Owner) → Raffle → Collaborator → Tickets`. The evolution is additive
> (populate `user_id`), not a schema rewrite.

---

## Analytics & Reports (Sprint 9)

Not a domain entity — a **read model**. `modules/analytics` owns no table and
introduces no new business rule; it aggregates the existing Raffle/Ticket/
Participant/Collaborator data into reporting projections (executive dashboard,
per-raffle/collaborator/participant reports, global top-N rankings and time
series) and exports them as Excel/PDF. Deliberately independent from
`modules/dashboard` (Sprint 5) so the two read models can evolve separately;
neither imports the other.

`received_revenue` reads as "money collected" but is derived from
`Ticket.status = PAID`, not a real transaction — it is the explicit seat left
for the future Payment entity (see below) to populate once it exists.

---

# Future Entities

These entities are not part of the MVP but must be considered in the architecture.

## User

Platform administrator.

---

## Payment

Tracks online payments.

---

## Notification

Emails

WhatsApp

SMS

Push Notifications

---

## Audit Log

Stores important business events.

---

# Entity Relationships

Organization

1 ---- * Raffle

Raffle

1 ---- * Ticket

Participant

1 ---- * Ticket

Ticket

* ---- 1 Raffle

Ticket

0..1 ---- 1 Participant

---

# Aggregate Roots

The following entities are aggregate roots.

- Organization
- Raffle
- Participant

Tickets should always be managed through a Raffle.

---

# Raffle Lifecycle

Draft

↓

Published

↓

Closed

↓

Archived

---

# Ticket Lifecycle

Available

↓

Reserved

↓

Paid (Future)

↓

Winner

or

↓

Cancelled

↓

Available

---

# Business Rules

## Organization

- An organization can own multiple raffles.
- A raffle belongs to only one organization.

---

## Raffle

- A raffle must have at least one ticket.
- A raffle cannot be published without generated tickets.
- A raffle cannot be deleted once tickets have participants.
- A closed raffle cannot receive new reservations.
- An archived raffle becomes read-only.

---

## Ticket

- Ticket numbers must be unique inside a raffle.
- A ticket belongs to only one raffle.
- A ticket can belong to only one participant.
- A winner must always be an existing ticket.
- A winning ticket cannot be deleted.

---

## Participant

- A participant can reserve multiple tickets.
- A participant cannot own duplicate ticket numbers in the same raffle.
- Participant information should remain even if the raffle closes.

---

# Invariants

These rules can never be violated.

- No duplicated ticket numbers.
- No duplicated winners.
- A ticket cannot belong to multiple participants.
- A closed raffle cannot accept reservations.
- Every winner must belong to a participant.
- Every ticket belongs to exactly one raffle.

---

# Domain Events (Future)

The architecture should support domain events.

Examples:

- RaffleCreated
- RafflePublished
- TicketReserved
- TicketReleased
- TicketPurchased
- WinnerSelected
- PaymentConfirmed
- NotificationSent

---

# Ubiquitous Language

Organization

The business that owns raffles.

---

Raffle

A numbered raffle.

---

Ticket

A numbered opportunity to participate.

---

Participant

A customer participating in a raffle.

---

Reservation

Temporary assignment of one or more tickets.

---

Winner

The participant owning the winning ticket.

---

Draw

The action of selecting the winning ticket.

---

# Domain Goals

The domain model must ensure:

- Consistency
- Simplicity
- Scalability
- Extensibility

Business rules always take precedence over technical convenience.