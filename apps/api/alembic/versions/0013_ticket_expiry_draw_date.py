"""backfill: align existing reserved tickets' expires_at with their raffle's draw_date

Revision ID: 0013_ticket_expiry_draw_date
Revises: 0012_collab_raffles_cascade
Create Date: 2026-07-31

Reserving/assigning a ticket used to set expires_at to a fixed 48h-from-now
TTL (app/core/config.py's now-removed reservation_ttl_hours), shared by both
the public self-service reservation flow and admin actions (an organizer
manually assigning a participant to a ticket). Any admin-assigned ticket left
unpaid for 48h was silently released back to AVAILABLE by the
reservation-expiry sweep, wiping its participant and collaborator — reported
in production as tickets/participants disappearing on their own.

The fix (see TicketService.reserve/assign_participant and
TicketUseCases._reservation_expiry) makes expires_at track the raffle's own
draw_date going forward: an unpaid ticket is only released once the raffle
is actually about to be drawn, not on a short fixed timer. This migration
backfills that same invariant onto every currently RESERVED ticket, so rows
created under the old behavior don't keep expiring on their stale
48h-from-reservation timestamp.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0013_ticket_expiry_draw_date"
down_revision: str | None = "0012_collab_raffles_cascade"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE tickets
        SET expires_at = raffles.draw_date
        FROM raffles
        WHERE tickets.raffle_id = raffles.id
          AND tickets.status = 'reserved'
          AND tickets.expires_at IS NOT NULL
          AND tickets.expires_at IS DISTINCT FROM raffles.draw_date
        """
    )


def downgrade() -> None:
    # The original 48h-from-reservation timestamps aren't recoverable (they
    # were never stored anywhere but the overwritten column) — this backfill
    # is intentionally irreversible.
    pass
