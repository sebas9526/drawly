"""collaborators table + tickets.collaborator_id

Revision ID: 0005_collaborators
Revises: 0004_users_and_ownership
Create Date: 2026-07-04

Sprint 7: sales collaborators per raffle. Creates the ``collaborators`` table
(owner_id denormalized for tenant scoping; nullable user_id reserved so a
collaborator can later become a login user) and adds a nullable
``tickets.collaborator_id`` FK crediting the seller of a reservation/sale.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_collaborators"
down_revision: str | None = "0004_users_and_ownership"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "collaborators",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=True),
        sa.Column("raffle_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=150), nullable=True),
        sa.Column("color", sa.String(length=9), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["raffle_id"], ["raffles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_collaborators_owner_id", "collaborators", ["owner_id"])
    op.create_index("ix_collaborators_raffle_id", "collaborators", ["raffle_id"])
    op.create_index("ix_collaborators_user_id", "collaborators", ["user_id"])
    op.create_index("ix_collaborators_email", "collaborators", ["email"])
    op.create_index("ix_collaborators_is_active", "collaborators", ["is_active"])

    op.add_column("tickets", sa.Column("collaborator_id", sa.Uuid(), nullable=True))
    op.create_index("ix_tickets_collaborator_id", "tickets", ["collaborator_id"])
    op.create_foreign_key(
        "fk_tickets_collaborator_id", "tickets", "collaborators", ["collaborator_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_tickets_collaborator_id", "tickets", type_="foreignkey")
    op.drop_index("ix_tickets_collaborator_id", table_name="tickets")
    op.drop_column("tickets", "collaborator_id")

    op.drop_index("ix_collaborators_is_active", table_name="collaborators")
    op.drop_index("ix_collaborators_email", table_name="collaborators")
    op.drop_index("ix_collaborators_user_id", table_name="collaborators")
    op.drop_index("ix_collaborators_raffle_id", table_name="collaborators")
    op.drop_index("ix_collaborators_owner_id", table_name="collaborators")
    op.drop_table("collaborators")
