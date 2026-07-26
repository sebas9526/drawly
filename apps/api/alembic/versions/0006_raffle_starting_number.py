"""raffles.starting_number

Revision ID: 0006_raffle_starting_number
Revises: 0005_collaborators
Create Date: 2026-07-25

Lets an organizer choose whether ticket numbering starts at 0 or 1 (e.g. a
100-ticket raffle can generate "00".."99" instead of always "001".."100").
Fixed at raffle creation and never editable afterwards (enforced by
RaffleCreate/RaffleUpdate, same as every other numeric field in this table —
no DB-level CHECK constraint, consistent with total_tickets' ge=1).
Server default of 1 preserves the pre-existing numbering for every row
created before this migration.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_raffle_starting_number"
down_revision: str | None = "0005_collaborators"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "raffles",
        sa.Column("starting_number", sa.Integer(), nullable=False, server_default="1"),
    )


def downgrade() -> None:
    op.drop_column("raffles", "starting_number")
