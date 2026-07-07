"""Pure domain unit tests for the ticket state machine — no DB involved."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.modules.tickets.exceptions import (
    TicketImmutableError,
    TicketNotAvailableError,
    TicketNotReservedError,
)
from app.modules.tickets.models import Ticket, TicketStatus
from app.modules.tickets.services import TicketService

NOW = datetime(2026, 7, 2, 12, 0, tzinfo=UTC)
TTL = timedelta(hours=48)


def _ticket(status: TicketStatus = TicketStatus.AVAILABLE) -> Ticket:
    return Ticket(raffle_id=uuid.uuid4(), number=1, status=status)


def test_available_ticket_can_be_reserved() -> None:
    participant = uuid.uuid4()
    ticket = TicketService.reserve(_ticket(), now=NOW, ttl=TTL, participant_id=participant)

    assert ticket.status is TicketStatus.RESERVED
    assert ticket.participant_id == participant
    assert ticket.reserved_at == NOW
    assert ticket.expires_at == NOW + TTL


def test_reserved_ticket_cannot_be_reserved_again() -> None:
    with pytest.raises(TicketNotAvailableError):
        TicketService.reserve(_ticket(TicketStatus.RESERVED), now=NOW, ttl=TTL)


def test_paid_ticket_cannot_be_sold_twice() -> None:
    with pytest.raises(TicketNotAvailableError):
        TicketService.reserve(_ticket(TicketStatus.PAID), now=NOW, ttl=TTL)


def test_cancellation_returns_ticket_to_available_and_clears_participant() -> None:
    ticket = _ticket(TicketStatus.RESERVED)
    ticket.participant_id = uuid.uuid4()
    ticket.reserved_at = NOW
    ticket.expires_at = NOW + TTL

    TicketService.cancel_reservation(ticket, now=NOW)

    assert ticket.status is TicketStatus.AVAILABLE
    assert ticket.participant_id is None
    assert ticket.reserved_at is None
    assert ticket.expires_at is None


def test_available_ticket_cannot_be_cancelled() -> None:
    with pytest.raises(TicketNotReservedError):
        TicketService.cancel_reservation(_ticket(TicketStatus.AVAILABLE), now=NOW)


def test_paid_ticket_cannot_be_cancelled() -> None:
    with pytest.raises(TicketImmutableError):
        TicketService.cancel_reservation(_ticket(TicketStatus.PAID), now=NOW)


def test_reserved_ticket_can_be_marked_paid() -> None:
    ticket = _ticket(TicketStatus.RESERVED)
    ticket.expires_at = NOW + TTL

    TicketService.mark_as_paid(ticket, now=NOW)

    assert ticket.status is TicketStatus.PAID
    assert ticket.sold_at == NOW
    assert ticket.expires_at is None


def test_available_ticket_cannot_be_marked_paid() -> None:
    with pytest.raises(TicketNotReservedError):
        TicketService.mark_as_paid(_ticket(TicketStatus.AVAILABLE), now=NOW)


def test_paid_ticket_is_immutable_when_paid_again() -> None:
    with pytest.raises(TicketImmutableError):
        TicketService.mark_as_paid(_ticket(TicketStatus.PAID), now=NOW)
