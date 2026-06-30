# Database Migrations

Migration tool

Alembic

---

Rules

Never modify an existing migration.

Always create a new migration.

Every migration must be reversible.

Every migration must be reviewed before production.

Migration names

create_organizations_table

create_raffles_table

create_participants_table

create_tickets_table

add_ticket_price

add_public_slug

Example

alembic revision --autogenerate -m "create raffles table"

Apply

alembic upgrade head

Rollback

alembic downgrade -1