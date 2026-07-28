"""collaborator_raffles (many-to-many) + drop collaborators.raffle_id

Revision ID: 0011_collaborator_raffles
Revises: 0010_raffle_winner_and_closed_at
Create Date: 2026-07-28

A collaborator used to belong to exactly one raffle (collaborators.raffle_id,
required FK) — reusing the same salesperson across raffles meant creating a
duplicate row per raffle with no link between them. This introduces
collaborator_raffles as a proper many-to-many join (soft-delete-aware, same
audit-field shape as every other table — see CollaboratorRaffle), backfills
one link per existing collaborator from its old raffle_id, then drops that
column.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0011_collaborator_raffles"
down_revision: str | None = "0010_raffle_winner_and_closed_at"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "collaborator_raffles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("collaborator_id", sa.Uuid(), nullable=False),
        sa.Column("raffle_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["collaborator_id"], ["collaborators.id"]),
        sa.ForeignKeyConstraint(["raffle_id"], ["raffles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_collaborator_raffles_collaborator_id", "collaborator_raffles", ["collaborator_id"]
    )
    op.create_index("ix_collaborator_raffles_raffle_id", "collaborator_raffles", ["raffle_id"])
    op.create_index(
        "ix_collaborator_raffles_pair", "collaborator_raffles", ["collaborator_id", "raffle_id"]
    )

    # One link per existing collaborator, carrying its current raffle_id over.
    op.execute(
        """
        INSERT INTO collaborator_raffles
            (id, collaborator_id, raffle_id, created_at, updated_at, deleted_at)
        SELECT gen_random_uuid(), id, raffle_id, created_at, updated_at, deleted_at
        FROM collaborators
        """
    )

    op.drop_index("ix_collaborators_raffle_id", table_name="collaborators")
    op.drop_constraint("collaborators_raffle_id_fkey", "collaborators", type_="foreignkey")
    op.drop_column("collaborators", "raffle_id")


def downgrade() -> None:
    op.add_column("collaborators", sa.Column("raffle_id", sa.Uuid(), nullable=True))
    op.execute(
        """
        UPDATE collaborators
        SET raffle_id = (
            SELECT cr.raffle_id
            FROM collaborator_raffles cr
            WHERE cr.collaborator_id = collaborators.id AND cr.deleted_at IS NULL
            ORDER BY cr.created_at ASC
            LIMIT 1
        )
        """
    )
    op.alter_column("collaborators", "raffle_id", nullable=False)
    op.create_foreign_key(
        "collaborators_raffle_id_fkey", "collaborators", "raffles", ["raffle_id"], ["id"]
    )
    op.create_index("ix_collaborators_raffle_id", "collaborators", ["raffle_id"])

    op.drop_index("ix_collaborator_raffles_pair", table_name="collaborator_raffles")
    op.drop_index("ix_collaborator_raffles_raffle_id", table_name="collaborator_raffles")
    op.drop_index("ix_collaborator_raffles_collaborator_id", table_name="collaborator_raffles")
    op.drop_table("collaborator_raffles")
