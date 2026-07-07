"""Ticket domain service: the single owner of the ticket state machine.

Every transition rule from docs/02-architecture/DOMAIN_MODEL.md lives here and
operates on in-memory ``Ticket`` entities only — no repositories, no session —
so the rules are unit-testable without a database. Application/use-case code
loads and persists; this class decides what is *allowed*.
"""

import uuid
from datetime import datetime, timedelta

from app.modules.tickets.exceptions import (
    TicketImmutableError,
    TicketNotAvailableError,
    TicketNotReservedError,
)
from app.modules.tickets.models import Ticket, TicketStatus

# States a paid/winning ticket is locked into — it may not be modified or deleted.
_IMMUTABLE_STATES: frozenset[TicketStatus] = frozenset({TicketStatus.PAID, TicketStatus.WINNER})


class TicketService:
    @staticmethod
    def ensure_mutable(ticket: Ticket) -> None:
        if ticket.status in _IMMUTABLE_STATES:
            raise TicketImmutableError()

    @classmethod
    def reserve(
        cls,
        ticket: Ticket,
        *,
        now: datetime,
        ttl: timedelta,
        participant_id: uuid.UUID | None = None,
        collaborator_id: uuid.UUID | None = None,
    ) -> Ticket:
        """AVAILABLE -> RESERVED. A reserved/paid ticket cannot be reserved
        again (no double reservation, no double sale). ``collaborator_id`` credits
        the seller of the reservation (optional)."""
        if ticket.status is not TicketStatus.AVAILABLE:
            raise TicketNotAvailableError()
        ticket.status = TicketStatus.RESERVED
        ticket.participant_id = participant_id
        ticket.collaborator_id = collaborator_id
        ticket.reserved_at = now
        ticket.expires_at = now + ttl
        return ticket

    @classmethod
    def cancel_reservation(cls, ticket: Ticket, *, now: datetime) -> Ticket:
        """RESERVED -> AVAILABLE. Releases the ticket and wipes every link to
        the participant. A paid ticket cannot be cancelled."""
        cls.ensure_mutable(ticket)
        if ticket.status is not TicketStatus.RESERVED:
            raise TicketNotReservedError()
        ticket.status = TicketStatus.AVAILABLE
        ticket.participant_id = None
        ticket.collaborator_id = None
        ticket.reserved_at = None
        ticket.expires_at = None
        return ticket

    @classmethod
    def set_collaborator(cls, ticket: Ticket, *, collaborator_id: uuid.UUID | None) -> Ticket:
        """Assign or clear the collaborator (seller) credited on a ticket. Only a
        reserved ticket can be re-credited; a paid/winning ticket is immutable and
        an available ticket has no sale to credit."""
        cls.ensure_mutable(ticket)
        if ticket.status is not TicketStatus.RESERVED:
            raise TicketNotReservedError(
                "Only a reserved ticket can have its collaborator changed."
            )
        ticket.collaborator_id = collaborator_id
        return ticket

    @classmethod
    def assign_participant(
        cls,
        ticket: Ticket,
        *,
        participant_id: uuid.UUID,
        now: datetime,
        ttl: timedelta,
    ) -> Ticket:
        """Assign or change the participant on a ticket.

        AVAILABLE -> reserve it for the participant (RESERVED).
        RESERVED  -> change the participant (stays reserved).
        PAID/WINNER -> immutable (rejected). Participant existence is guaranteed
        by the DB foreign key at persist time.
        """
        cls.ensure_mutable(ticket)
        if ticket.status is TicketStatus.AVAILABLE:
            return cls.reserve(ticket, now=now, ttl=ttl, participant_id=participant_id)
        if ticket.status is TicketStatus.RESERVED:
            ticket.participant_id = participant_id
            return ticket
        raise TicketNotAvailableError(
            "Ticket cannot be assigned a participant in its current state."
        )

    @classmethod
    def unassign_participant(cls, ticket: Ticket, *, now: datetime) -> Ticket:
        """Remove the participant from a RESERVED ticket, releasing it back to
        AVAILABLE (same rule as cancelling a reservation). A paid ticket cannot
        be changed."""
        return cls.cancel_reservation(ticket, now=now)

    @classmethod
    def mark_as_paid(cls, ticket: Ticket, *, now: datetime) -> Ticket:
        """RESERVED -> PAID. Only a reserved ticket can be paid, which prevents
        paying an available ticket or paying twice."""
        cls.ensure_mutable(ticket)
        if ticket.status is not TicketStatus.RESERVED:
            raise TicketNotReservedError("Only a reserved ticket can be marked as paid.")
        ticket.status = TicketStatus.PAID
        ticket.sold_at = now
        ticket.expires_at = None  # a paid ticket no longer expires
        return ticket
