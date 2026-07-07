"""dashboard performance indexes

Revision ID: 0003_dashboard_indexes
Revises: 0002_participants
Create Date: 2026-07-03

Sprint 6: indexes that back the dashboard's "recent" ORDER BY ... LIMIT queries
(recent reservations by tickets.reserved_at, recent raffles by raffles.created_at).
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0003_dashboard_indexes"
down_revision: str | None = "0002_participants"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("ix_tickets_reserved_at", "tickets", ["reserved_at"])
    op.create_index("ix_raffles_created_at", "raffles", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_raffles_created_at", table_name="raffles")
    op.drop_index("ix_tickets_reserved_at", table_name="tickets")
