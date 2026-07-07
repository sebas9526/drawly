"""Analytics & Reports module (Sprint 9).

Independent read-model module: it owns its own aggregation queries over the
raffles/tickets/participants/collaborators tables rather than importing the
Sprint-7 `app.modules.dashboard` module, so the two can evolve separately.
Every query is owner-scoped and never mutates data.
"""
