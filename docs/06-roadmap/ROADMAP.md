# Drawly Roadmap

Version 1.0

---

# Phase 0 - Foundation

- Repository setup
- Documentation
- Architecture
- Database design
- API specification

Status

✅ Completed

---

# Phase 1 - Infrastructure

- Docker
- PostgreSQL
- FastAPI
- Next.js
- SQLModel
- Alembic
- CI/CD

---

# Phase 2 - Raffles Module

- CRUD Raffles
- Generate Tickets
- Publish Raffle
- Close Raffle

---

# Phase 3 - Participants Module

- Register Participant
- Assign Tickets
- Update Participant
- Delete Participant

---

# Phase 4 - Ticket Module

- Ticket Grid
- Ticket Reservation
- Reservation Cancellation
- Winner Selection

---

# Phase 5 - Dashboard

- Statistics
- Revenue
- Filters
- Search

---

# Phase 6 - Testing

- Unit Tests
- Integration Tests
- E2E Tests

---

# Phase 7 - Deployment

- Production
- Domain
- SSL
- Monitoring

---

# Phase 8 - SaaS

- Authentication ✅ (cookie JWT + Argon2, login/register)
- Multi-tenancy / per-user data isolation ✅ (`owner_id` on raffles, tickets, participants)
- Public landing page ✅
- Sales collaborators per raffle ✅ (CRUD, ticket crediting, per-collaborator stats; `user_id` reserved for future collaborator login)
- Admin panel UX overhaul ✅ (Sprint 8: dashboard quick actions, raffle/ticket/participant/collaborator screens, referral links)
- Reports ✅ (Sprint 9 — see Phase 9 below)
- Analytics ✅ (Sprint 9 — see Phase 9 below)
- Organizations
- Payments
- Notifications
- Password recovery (forgot/reset) — pending
- Roles & permissions (Owner, Admin, Seller, Viewer) — pending

---

# Phase 9 - Analytics & Reports (Sprint 9)

- Independent `modules/analytics` backend module (read-only, no cross-import
  from `modules/dashboard`) ✅
- Executive dashboard KPIs (raffles, tickets, participants, collaborators,
  expected/received revenue, % sold/reserved) ✅
- Per-raffle report (counts, % sold, expected revenue, top collaborators/
  participants) ✅
- Collaborator report (sales, reservations, participants served, expected
  amount, participation %, ranking) ✅
- Participant report (purchases, tickets, amount invested, last purchase,
  raffle count) ✅
- Global reports (top collaborators/raffles/participants, sales/reservations
  per day, ticket status distribution) ✅
- Filters on every endpoint: date range, raffle, ticket status, collaborator ✅
- Excel (openpyxl) and PDF (reportlab) export for every report ✅
- Frontend `/reports` section (Resumen, Rifas, Colaboradores, Participantes)
  reusing the existing design system — no new charting library, hand-rolled
  SVG `DonutChart`/`BarChart` added to `@drawly/ui` ✅
- `received_revenue` is derived from ticket status (PAID), not a real
  transaction — the explicit seat for the future Payments module (see Phase 8) ✅
- Known gaps carried to a future sprint: "cantidad de clientes" on the raffle-
  level collaborator ranking, `WINNER`/`CANCELLED` ticket states are defined
  but never actually set by any use case yet (draw/cancellation features don't
  exist), and the participants report has no pagination (fine at current
  scale, would need one before very large accounts)