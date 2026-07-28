"""raffles.closed_at, raffles.winner_ticket_id

Revision ID: 0010_raffle_winner_and_closed_at
Revises: 0009_raffle_slug_not_unique
Create Date: 2026-07-28

Supports manual winner registration: `winner_ticket_id` records the last
winner-registration attempt (valid or not — validity is derived from that
ticket's own status), and `closed_at` is set only once a *valid* winner
closes the raffle. `closed_at` is what the cleanup sweep uses to soft-delete
a concluded raffle (and its tickets) a fixed grace period later.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0010_raffle_winner_and_closed_at"
down_revision: str | None = "0009_raffle_slug_not_unique"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "raffles",
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "raffles",
        sa.Column("winner_ticket_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_raffles_winner_ticket_id", "raffles", "tickets", ["winner_ticket_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_raffles_winner_ticket_id", "raffles", type_="foreignkey")
    op.drop_column("raffles", "winner_ticket_id")
    op.drop_column("raffles", "closed_at")
