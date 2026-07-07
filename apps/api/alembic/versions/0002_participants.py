"""participants table + tickets.participant_id FK

Revision ID: 0002_participants
Revises: 0001_raffles_and_tickets
Create Date: 2026-07-03

Sprint 4: creates the participants table and promotes tickets.participant_id to
a real foreign key (the participants module now exists). Soft delete + audit
fields per docs/03-database/DATABASE_DESIGN.md. Phone is intentionally NOT unique
at the DB level (uniqueness is enforced in the domain among active participants).
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_participants"
down_revision: str | None = "0001_raffles_and_tickets"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "participants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=True),
        sa.Column("document", sa.String(length=50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=80), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_participants_phone", "participants", ["phone"])
    op.create_index("ix_participants_email", "participants", ["email"])
    op.create_index("ix_participants_document", "participants", ["document"])

    # Promote tickets.participant_id to a real FK now that participants exists.
    op.create_foreign_key(
        "fk_tickets_participant_id",
        "tickets",
        "participants",
        ["participant_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_tickets_participant_id", "tickets", type_="foreignkey")
    op.drop_index("ix_participants_document", table_name="participants")
    op.drop_index("ix_participants_email", table_name="participants")
    op.drop_index("ix_participants_phone", table_name="participants")
    op.drop_table("participants")
