"""users table + owner_id ownership columns

Revision ID: 0004_users_and_ownership
Revises: 0003_dashboard_indexes
Create Date: 2026-07-03

Sprint (Auth + multi-tenancy): creates the ``users`` table and adds a nullable
``owner_id`` FK to raffles, participants and tickets so every admin query can be
scoped to the authenticated user. Nullable so pre-existing rows (created before
auth) remain valid; new rows always carry an owner. Soft delete + audit fields
per docs/03-database/DATABASE_DESIGN.md.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_users_and_ownership"
down_revision: str | None = "0003_dashboard_indexes"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # owner_id on each owned aggregate (nullable + FK to users.id).
    for table in ("raffles", "participants", "tickets"):
        op.add_column(table, sa.Column("owner_id", sa.Uuid(), nullable=True))
        op.create_index(f"ix_{table}_owner_id", table, ["owner_id"])
        op.create_foreign_key(f"fk_{table}_owner_id", table, "users", ["owner_id"], ["id"])


def downgrade() -> None:
    for table in ("tickets", "participants", "raffles"):
        op.drop_constraint(f"fk_{table}_owner_id", table, type_="foreignkey")
        op.drop_index(f"ix_{table}_owner_id", table_name=table)
        op.drop_column(table, "owner_id")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
