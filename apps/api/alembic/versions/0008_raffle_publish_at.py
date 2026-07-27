"""raffles.publish_at

Revision ID: 0008_raffle_publish_at
Revises: 0007_raffle_draw_date_timezone
Create Date: 2026-07-27

Optional scheduled activation date for a raffle. NULL preserves today's
behavior (publish only via the explicit manual action); when set, the
in-process sweep publishes the raffle automatically once the date arrives,
provided tickets have already been generated.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008_raffle_publish_at"
down_revision: str | None = "0007_raffle_draw_date_timezone"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "raffles",
        sa.Column("publish_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("raffles", "publish_at")
