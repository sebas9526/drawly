"""raffles.public_slug not globally unique

Revision ID: 0009_raffle_slug_not_unique
Revises: 0008_raffle_publish_at
Create Date: 2026-07-27

`ix_raffles_public_slug` was a table-wide UNIQUE index, but slug uniqueness
is (and always was) actually enforced at the application layer scoped to
non-deleted rows (RaffleRepository.exists_slug + RaffleUseCases._unique_slug)
— the same pattern already used for participants.phone. The DB-level UNIQUE
constraint outlived a soft-deleted raffle and permanently blocked reusing its
slug, causing a 500 (IntegrityError) the moment someone deleted a raffle and
created a new one with the same title. Drops the unique constraint and
recreates the index as a plain (non-unique) one, matching
ix_participants_phone.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0009_raffle_slug_not_unique"
down_revision: str | None = "0008_raffle_publish_at"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("ix_raffles_public_slug", table_name="raffles")
    op.create_index("ix_raffles_public_slug", "raffles", ["public_slug"])


def downgrade() -> None:
    op.drop_index("ix_raffles_public_slug", table_name="raffles")
    op.create_index("ix_raffles_public_slug", "raffles", ["public_slug"], unique=True)
