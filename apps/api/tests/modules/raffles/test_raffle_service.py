from datetime import UTC

import pytest

from app.modules.raffles.exceptions import RaffleNotEditableError
from app.modules.raffles.models import RaffleStatus
from app.modules.raffles.schemas import RaffleUpdate
from app.modules.raffles.services import RaffleService
from app.modules.raffles.validators import slugify


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Gran Rifa Benéfica 2026", "gran-rifa-benefica-2026"),
        ("  Hello   World  ", "hello-world"),
        ("Rifa #1 -- Súper!", "rifa-1-super"),
    ],
)
def test_slugify_is_deterministic_kebab_case(value: str, expected: str) -> None:
    assert slugify(value) == expected


def test_slug_candidate_falls_back_when_empty() -> None:
    assert RaffleService.slug_candidate("###") == "raffle"


def test_published_raffle_is_not_editable() -> None:
    from datetime import datetime

    from app.modules.raffles.models import Raffle

    raffle = Raffle(
        title="X",
        total_tickets=10,
        draw_date=datetime(2026, 8, 1, tzinfo=UTC),
        status=RaffleStatus.PUBLISHED,
        public_slug="x",
    )
    with pytest.raises(RaffleNotEditableError):
        RaffleService.apply_update(raffle, RaffleUpdate(title="new"))


def test_ensure_can_publish_requires_draft() -> None:
    from datetime import datetime

    from app.modules.raffles.exceptions import RaffleNotPublishableError
    from app.modules.raffles.models import Raffle

    raffle = Raffle(
        title="X",
        total_tickets=10,
        draw_date=datetime(2026, 8, 1, tzinfo=UTC),
        status=RaffleStatus.PUBLISHED,
        public_slug="x",
    )
    with pytest.raises(RaffleNotPublishableError):
        RaffleService.ensure_can_publish(raffle, has_tickets=True, now=datetime.now(UTC))


def test_ensure_can_publish_requires_tickets() -> None:
    from datetime import datetime

    from app.modules.raffles.exceptions import RaffleNotPublishableError
    from app.modules.raffles.models import Raffle

    raffle = Raffle(
        title="X",
        total_tickets=10,
        draw_date=datetime(2026, 8, 1, tzinfo=UTC),
        status=RaffleStatus.DRAFT,
        public_slug="x",
    )
    with pytest.raises(RaffleNotPublishableError):
        RaffleService.ensure_can_publish(raffle, has_tickets=False, now=datetime.now(UTC))


def test_publish_transitions_to_published() -> None:
    from datetime import datetime

    from app.modules.raffles.models import Raffle

    raffle = Raffle(
        title="X",
        total_tickets=10,
        draw_date=datetime(2026, 8, 1, tzinfo=UTC),
        status=RaffleStatus.DRAFT,
        public_slug="x",
    )
    RaffleService.ensure_can_publish(raffle, has_tickets=True, now=datetime.now(UTC))
    RaffleService.publish(raffle)
    assert raffle.status is RaffleStatus.PUBLISHED


def test_ensure_can_publish_blocks_manual_publish_before_the_schedule() -> None:
    """Regression test: manual publish used to ignore publish_at entirely,
    letting an admin jump a scheduled raffle live early — exactly what
    happened in production (see conversation)."""
    from datetime import datetime, timedelta

    from app.modules.raffles.exceptions import RaffleNotPublishableError
    from app.modules.raffles.models import Raffle

    now = datetime(2026, 7, 28, tzinfo=UTC)
    raffle = Raffle(
        title="X",
        total_tickets=10,
        draw_date=datetime(2026, 9, 1, tzinfo=UTC),
        publish_at=now + timedelta(days=4),
        status=RaffleStatus.DRAFT,
        public_slug="x",
    )
    with pytest.raises(RaffleNotPublishableError):
        RaffleService.ensure_can_publish(raffle, has_tickets=True, now=now)


def test_ensure_can_publish_allows_manual_publish_once_the_schedule_arrives() -> None:
    from datetime import datetime, timedelta

    from app.modules.raffles.models import Raffle

    now = datetime(2026, 7, 28, tzinfo=UTC)
    raffle = Raffle(
        title="X",
        total_tickets=10,
        draw_date=datetime(2026, 9, 1, tzinfo=UTC),
        publish_at=now - timedelta(minutes=1),
        status=RaffleStatus.DRAFT,
        public_slug="x",
    )
    RaffleService.ensure_can_publish(raffle, has_tickets=True, now=now)
    RaffleService.publish(raffle)
    assert raffle.status is RaffleStatus.PUBLISHED
