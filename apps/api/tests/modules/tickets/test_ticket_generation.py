import uuid
from datetime import UTC, datetime

import pytest

from app.modules.tickets.exceptions import InvalidTicketQuantityError
from app.modules.tickets.models import TicketStatus
from app.modules.tickets.services import TicketGenerationService

NOW = datetime(2026, 7, 2, 12, 0, tzinfo=UTC)


@pytest.mark.parametrize("quantity", [1, 100, 500, 1000, 5000])
def test_generation_produces_exactly_requested_quantity(quantity: int) -> None:
    raffle_id = uuid.uuid4()
    tickets = TicketGenerationService.generate(raffle_id, quantity, now=NOW)

    assert len(tickets) == quantity
    numbers = [ticket.number for ticket in tickets]
    assert numbers == list(range(1, quantity + 1))  # sequential, no gaps
    assert len(set(numbers)) == quantity  # unique
    assert all(ticket.status is TicketStatus.AVAILABLE for ticket in tickets)
    assert all(ticket.raffle_id == raffle_id for ticket in tickets)


def test_generation_rejects_non_positive_quantity() -> None:
    with pytest.raises(InvalidTicketQuantityError):
        TicketGenerationService.generate(uuid.uuid4(), 0, now=NOW)
