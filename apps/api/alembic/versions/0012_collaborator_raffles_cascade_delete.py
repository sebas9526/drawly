"""collaborator_raffles.raffle_id ON DELETE CASCADE

Revision ID: 0012_collaborator_raffles_cascade_delete
Revises: 0011_collaborator_raffles
Create Date: 2026-07-28

"Eliminar rifa" changed from soft-delete to a real, permanent delete
(RaffleUseCases.delete now hard-deletes the raffle row and its tickets
explicitly). collaborator_raffles is a pure join table with no business logic
of its own, so instead of teaching the raffles module about it too (a new
cross-module port just for cleanup), the DB cascades it automatically when
the raffle row goes away — the standard, low-risk use of ON DELETE CASCADE
for a join table specifically (tickets, which does carry real history, is
still deleted explicitly rather than cascaded).
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0012_collaborator_raffles_cascade_delete"
down_revision: str | None = "0011_collaborator_raffles"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "collaborator_raffles_raffle_id_fkey", "collaborator_raffles", type_="foreignkey"
    )
    op.create_foreign_key(
        "collaborator_raffles_raffle_id_fkey",
        "collaborator_raffles",
        "raffles",
        ["raffle_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "collaborator_raffles_raffle_id_fkey", "collaborator_raffles", type_="foreignkey"
    )
    op.create_foreign_key(
        "collaborator_raffles_raffle_id_fkey",
        "collaborator_raffles",
        "raffles",
        ["raffle_id"],
        ["id"],
    )
