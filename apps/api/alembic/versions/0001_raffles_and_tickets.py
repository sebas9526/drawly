"""raffles and tickets tables

Revision ID: 0001_raffles_and_tickets
Revises:
Create Date: 2026-07-02

Creates the raffles and tickets tables for Sprint 3 (Ticket Management).
Follows docs/03-database/DATABASE_DESIGN.md: UUID PKs, audit fields, soft delete,
UNIQUE(raffle_id, number), every FK indexed. participant_id is a nullable UUID
without a FK for now (the participants module does not exist yet).
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_raffles_and_tickets"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "raffles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("prize", sa.Text(), nullable=False),
        sa.Column("cover_image", sa.Text(), nullable=True),
        sa.Column("ticket_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total_tickets", sa.Integer(), nullable=False),
        sa.Column("draw_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("public_slug", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_raffles_organization_id", "raffles", ["organization_id"])
    op.create_index("ix_raffles_status", "raffles", ["status"])
    op.create_index("ix_raffles_public_slug", "raffles", ["public_slug"], unique=True)

    op.create_table(
        "tickets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("raffle_id", sa.Uuid(), nullable=False),
        sa.Column("participant_id", sa.Uuid(), nullable=True),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("reserved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sold_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("winner_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["raffle_id"], ["raffles.id"], name="fk_tickets_raffle_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("raffle_id", "number", name="uq_ticket_raffle_number"),
    )
    op.create_index("ix_tickets_raffle_id", "tickets", ["raffle_id"])
    op.create_index("ix_tickets_participant_id", "tickets", ["participant_id"])
    op.create_index("ix_tickets_number", "tickets", ["number"])
    op.create_index("ix_tickets_status", "tickets", ["status"])


def downgrade() -> None:
    op.drop_index("ix_tickets_status", table_name="tickets")
    op.drop_index("ix_tickets_number", table_name="tickets")
    op.drop_index("ix_tickets_participant_id", table_name="tickets")
    op.drop_index("ix_tickets_raffle_id", table_name="tickets")
    op.drop_table("tickets")

    op.drop_index("ix_raffles_public_slug", table_name="raffles")
    op.drop_index("ix_raffles_status", table_name="raffles")
    op.drop_index("ix_raffles_organization_id", table_name="raffles")
    op.drop_table("raffles")
