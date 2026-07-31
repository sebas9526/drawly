"""Pure domain unit tests for assigning/removing a participant on a ticket."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.modules.tickets.exceptions import TicketImmutableError, TicketNotReservedError
from app.modules.tickets.models import Ticket, TicketStatus
from app.modules.tickets.services import TicketService

NOW = datetime(2026, 7, 3, 12, 0, tzinfo=UTC)
TTL = timedelta(hours=48)


def _ticket(status: TicketStatus = TicketStatus.AVAILABLE) -> Ticket:
    return Ticket(raffle_id=uuid.uuid4(), number=1, status=status)


def test_assign_to_available_reserves_for_participant() -> None:
    participant = uuid.uuid4()
    ticket = TicketService.assign_participant(
        _ticket(), participant_id=participant, now=NOW, expires_at=NOW + TTL
    )
    assert ticket.status is TicketStatus.RESERVED
    assert ticket.participant_id == participant
    assert ticket.reserved_at == NOW
    assert ticket.expires_at == NOW + TTL


def test_assign_without_a_known_draw_date_never_expires() -> None:
    """Regression: a ticket's expires_at is the raffle's own draw_date — if
    that's unknown (missing raffle), the assignment must not carry a made-up
    expiry that could silently release it (with the participant/collaborator
    wiped) via the reservation-expiry sweep."""
    participant = uuid.uuid4()
    ticket = TicketService.assign_participant(
        _ticket(), participant_id=participant, now=NOW, expires_at=None
    )
    assert ticket.status is TicketStatus.RESERVED
    assert ticket.expires_at is None


def test_assign_to_reserved_changes_participant() -> None:
    ticket = _ticket(TicketStatus.RESERVED)
    ticket.participant_id = uuid.uuid4()
    ticket.reserved_at = NOW
    new_participant = uuid.uuid4()

    TicketService.assign_participant(
        ticket, participant_id=new_participant, now=NOW, expires_at=NOW + TTL
    )

    assert ticket.status is TicketStatus.RESERVED
    assert ticket.participant_id == new_participant


def test_assign_to_paid_ticket_is_rejected() -> None:
    with pytest.raises(TicketImmutableError):
        TicketService.assign_participant(
            _ticket(TicketStatus.PAID), participant_id=uuid.uuid4(), now=NOW, expires_at=NOW + TTL
        )


def test_unassign_releases_ticket_to_available() -> None:
    ticket = _ticket(TicketStatus.RESERVED)
    ticket.participant_id = uuid.uuid4()
    ticket.reserved_at = NOW
    ticket.expires_at = NOW + TTL

    TicketService.unassign_participant(ticket, now=NOW)

    assert ticket.status is TicketStatus.AVAILABLE
    assert ticket.participant_id is None
    assert ticket.reserved_at is None


def test_unassign_paid_ticket_is_rejected() -> None:
    with pytest.raises(TicketImmutableError):
        TicketService.unassign_participant(_ticket(TicketStatus.PAID), now=NOW)


def test_unassign_available_ticket_is_rejected() -> None:
    with pytest.raises(TicketNotReservedError):
        TicketService.unassign_participant(_ticket(TicketStatus.AVAILABLE), now=NOW)
