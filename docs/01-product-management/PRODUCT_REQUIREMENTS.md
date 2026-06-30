# Product Requirements Document (PRD)

# Drawly MVP

---

# Objective

Develop the first production-ready version of Drawly.

The MVP should allow organizers to create, publish, and manage numbered raffles while participants can reserve available ticket numbers.

---

# Functional Requirements

## Raffles

The administrator can:

- Create raffles
- Edit raffles
- Delete raffles
- Publish raffles
- Close raffles
- Select winners

---

Each raffle contains:

- Title
- Description
- Prize
- Cover Image
- Ticket Price
- Number of Tickets
- Draw Date
- Status
- Public URL

---

## Ticket Generation

The system automatically generates numbered tickets.

Example:

100 tickets

001
002
...
100

1000 tickets

0001
0002
...
1000

---

Each ticket has one status.

Available

Reserved

Sold

Cancelled

Winner

---

## Participants

Participants can:

Open a public raffle.

Select one or multiple tickets.

Complete a registration form.

Reserve selected tickets.

---

Participant Information

- Full Name
- Phone Number
- Email (optional)
- Address
- City
- Notes

---

## Dashboard

Administrator dashboard includes:

- Active raffles
- Closed raffles
- Statistics
- Search
- Filters

---

Inside each raffle:

Participants table

Ticket grid

Statistics

Winner

Revenue

---

# Business Rules

A ticket cannot belong to two participants.

Deleted participants release their tickets.

Closed raffles cannot receive new participants.

Only available tickets can be reserved.

Winning ticket must belong to an existing participant.

---

# Non Functional Requirements

Responsive UI.

Fast API responses.

Strict typing.

Dockerized environment.

REST API.

Clean Architecture.

Modular design.

---

# MVP Scope

Included

✅ Raffle management

✅ Ticket management

✅ Participant registration

✅ Winner selection

Excluded

❌ Payments

❌ Authentication

❌ Notifications

❌ Reports

❌ Mobile App

❌ AI

---

# Acceptance Criteria

The MVP is complete when:

An organizer can create a raffle.

Participants can reserve tickets.

No duplicated tickets exist.

The administrator can select a winner.

The application is deployable.