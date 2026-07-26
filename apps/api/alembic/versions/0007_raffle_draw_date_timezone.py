"""raffles.draw_date timezone fix

Revision ID: 0007_raffle_draw_date_timezone
Revises: 0006_raffle_starting_number
Create Date: 2026-07-25

`draw_date` was declared as a plain `datetime` on the `Raffle` model (missing
the `sa_type=TZ_DATETIME` every other timestamp column in the codebase uses),
so it was created as `TIMESTAMP WITHOUT TIME ZONE`. Every request sends a
tz-aware value, which asyncpg rejects outright against a naive column — this
broke raffle creation against real Postgres (invisible under the SQLite test
suite, which doesn't enforce the distinction). Existing naive values are
assumed to already represent UTC instants (the only timezone this app has
ever run in), so they're reinterpreted with `AT TIME ZONE 'UTC'` rather than
shifted.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0007_raffle_draw_date_timezone"
down_revision: str | None = "0006_raffle_starting_number"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE raffles "
        "ALTER COLUMN draw_date TYPE TIMESTAMP WITH TIME ZONE "
        "USING draw_date AT TIME ZONE 'UTC'"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE raffles "
        "ALTER COLUMN draw_date TYPE TIMESTAMP WITHOUT TIME ZONE "
        "USING draw_date AT TIME ZONE 'UTC'"
    )
