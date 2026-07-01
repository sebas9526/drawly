# Business Modules

No business modules exist yet (see CLAUDE.md — infrastructure first).

Per `docs/02-architecture/ARCHITECTURE.md`, each module added here must be self-contained:

```
modules/
  <module_name>/
    routers/
    schemas/
    models/
    services/
    repositories/
    dependencies/
    exceptions/
    validators/
    tests/
```

Modules depend on `app/core`, `app/database`, and `app/api` (shared infra), never on each other directly.
