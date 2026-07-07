# Business Modules

Per `docs/02-architecture/ARCHITECTURE.md`, each module is self-contained:

```
modules/
  <module_name>/
    routers/
    schemas/
    models/
    services/       # domain rules (pure, no I/O)
    use_cases/      # application services (orchestration + transactions)
    repositories/
    dependencies/
    exceptions/
    validators/
```

Modules depend on `app/core`, `app/database`, and `app/api` (shared infra).
They never import each other's internals — cross-module collaboration goes
through a service/port only.

## Layering

- `services/` hold **domain rules** and operate on in-memory entities (e.g. the
  ticket state machine), so they are unit-testable without a database.
- `use_cases/` are **application services**: they load/persist via repositories,
  own the transaction boundary, and delegate rules to the domain services.
- `routers/` are thin controllers: parse the request, call a use case, wrap the
  result in the standard response envelope. No business logic.

## Modules

- **raffles** — raffle aggregate root. Create/list/get/update plus the explicit
  `POST /raffles/{id}/tickets` generation action.
- **tickets** — full ticket lifecycle: generation, reserve, cancel, mark-paid,
  assign/remove participant, list, list-available, detail. Owns `TicketStatus`
  and every transition rule.
- **participants** — participant CRUD + search, soft delete (blocked while the
  participant has tickets), and ticket history.
- **public** — unauthenticated reservation portal. A thin read/orchestration
  layer (no tables of its own): view a published raffle, list ticket
  availability, and reserve. It reuses the other modules' domain logic and never
  duplicates business rules or admin endpoints.
- **collaborators** — sales collaborator CRUD, scoped to a single raffle each.
  Tickets credit a collaborator via `tickets.collaborator_id` (nullable); stats
  are derived, not stored.
- **dashboard** — admin reporting **read model** (no tables of its own). Composes
  efficient grouped aggregate queries over raffles/tickets/participants (counts +
  sums in a handful of statements, not per-metric COUNT(*)) and returns the whole
  overview in one request. Read-only; holds no business rules.
- **analytics** — reporting **read model** (Sprint 9, no tables of its own).
  Executive dashboard KPIs, per-raffle/collaborator/participant reports, global
  top-N rankings + time series, and Excel/PDF export. Deliberately independent
  of `dashboard` — no cross-import either way — so the two can evolve on their
  own schedules.

### Cross-module dependencies (ports, all acyclic)

Modules never import each other's internals; collaboration goes through a port
(Dependency Inversion) wired only in the consumer's `dependencies` composition
root. `TicketUseCases` structurally satisfies both ports below.

- **raffles → tickets**: ticket generation belongs to the raffle aggregate, so
  raffles provisions tickets via the `TicketProvisioning` port
  (`raffles/services/ports.py`).
- **participants → tickets**: participants read ticket counts + history via the
  `ParticipantTickets` port (`participants/services/ports.py`).

- **public → raffles, tickets, participants**: the portal orchestrates the three
  via the `PublicRaffles` / `PublicTickets` / `PublicParticipants` ports
  (`public/services/ports.py`), each satisfied by the respective use case and
  wired in `public/dependencies` (which share one request-scoped session, so a
  reservation runs on a single connection).

Direction is one-way: `raffles → tickets`, `participants → tickets`, and
`public → {raffles, tickets, participants}`; tickets imports none of them.
Ticket→participant referential integrity is enforced by the DB foreign key (a
violation surfaces as a clean 404), so the tickets module stays decoupled from
participants. Concurrent public reservations are serialized by a row lock
(`SELECT ... FOR UPDATE`) so a ticket can't be reserved twice.

## Tests

Module tests live under the single collected test root
`apps/api/tests/modules/<module>/` (mirroring the source tree) so pytest's
configured `testpaths = ["tests"]` picks them up with no extra config. Pure
domain tests need no database; API-flow tests run against in-memory SQLite via a
`get_session` dependency override (`tests/modules/conftest.py`).
