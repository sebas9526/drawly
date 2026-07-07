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
        RaffleService.ensure_can_publish(raffle, has_tickets=True)


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
        RaffleService.ensure_can_publish(raffle, has_tickets=False)


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
    RaffleService.ensure_can_publish(raffle, has_tickets=True)
    RaffleService.publish(raffle)
    assert raffle.status is RaffleStatus.PUBLISHED
