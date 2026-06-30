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
- drawDate
- status
- publicSlug
- createdAt
- updatedAt

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
- soldAt
- winnerAt

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
- address
- city
- notes
- createdAt

### Relationships

Participant

→ owns many Tickets

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