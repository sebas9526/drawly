"""Ticket domain service: the single owner of the ticket state machine.

Every transition rule from docs/02-architecture/DOMAIN_MODEL.md lives here and
operates on in-memory ``Ticket`` entities only — no repositories, no session —
so the rules are unit-testable without a database. Application/use-case code
loads and persists; this class decides what is *allowed*.
"""

import uuid
from datetime import datetime

from app.modules.raffles.models import RaffleStatus
from app.modules.tickets.exceptions import (
    RaffleNotOpenForTicketsError,
    TicketImmutableError,
    TicketNotAvailableError,
    TicketNotPaidError,
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

    @staticmethod
    def ensure_raffle_open(raffle_status: RaffleStatus | None) -> None:
        """A ticket can only be reserved, paid, or assigned a participant once
        its raffle is actually published — this blocks admin pre-arranging
        (and self-service, though the public flow already 404s pre-publish)
        on a raffle still in draft, including one waiting on a scheduled
        publish_at. ``None`` (raffle missing/deleted) is treated the same as
        not open."""
        if raffle_status is not RaffleStatus.PUBLISHED:
            raise RaffleNotOpenForTicketsError()

    @classmethod
    def reserve(
        cls,
        ticket: Ticket,
        *,
        now: datetime,
        expires_at: datetime | None,
        participant_id: uuid.UUID | None = None,
        collaborator_id: uuid.UUID | None = None,
    ) -> Ticket:
        """AVAILABLE -> RESERVED. A reserved/paid ticket cannot be reserved
        again (no double reservation, no double sale). ``collaborator_id``
        credits the seller of the reservation (optional). ``expires_at`` is
        the raffle's own draw_date (set by the caller) — an unpaid ticket is
        only released once the raffle is actually about to be drawn, never on
        a short fixed timer; ``None`` means it never auto-expires (e.g. the
        raffle has no known draw_date)."""
        if ticket.status is not TicketStatus.AVAILABLE:
            raise TicketNotAvailableError()
        ticket.status = TicketStatus.RESERVED
        ticket.participant_id = participant_id
        ticket.collaborator_id = collaborator_id
        ticket.reserved_at = now
        ticket.expires_at = expires_at
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
        expires_at: datetime | None,
    ) -> Ticket:
        """Assign or change the participant on a ticket.

        AVAILABLE -> reserve it for the participant (RESERVED).
        RESERVED  -> change the participant (stays reserved).
        PAID/WINNER -> immutable (rejected). Participant existence is guaranteed
        by the DB foreign key at persist time.
        """
        cls.ensure_mutable(ticket)
        if ticket.status is TicketStatus.AVAILABLE:
            return cls.reserve(
                ticket, now=now, expires_at=expires_at, participant_id=participant_id
            )
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
    def is_expired(cls, ticket: Ticket, *, now: datetime) -> bool:
        """A RESERVED ticket whose TTL (set on reserve) has elapsed."""
        return (
            ticket.status is TicketStatus.RESERVED
            and ticket.expires_at is not None
            and ticket.expires_at <= now
        )

    @classmethod
    def release_expired(cls, ticket: Ticket, *, now: datetime) -> Ticket:
        """RESERVED (past its TTL) -> AVAILABLE. Same effect as an explicit
        cancellation, triggered by the sweep instead of a user action."""
        if not cls.is_expired(ticket, now=now):
            raise TicketNotReservedError("Ticket is not an expired reservation.")
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

    @staticmethod
    def mark_as_winner(ticket: Ticket, *, now: datetime) -> Ticket:
        """PAID -> WINNER. Deliberately does not go through ensure_mutable —
        a paid ticket being IMMUTABLE is exactly the precondition here, not a
        block. Only the raffle-level winner-registration flow calls this,
        after confirming the ticket is paid (RaffleUseCases.register_winner)."""
        if ticket.status is not TicketStatus.PAID:
            raise TicketNotPaidError()
        ticket.status = TicketStatus.WINNER
        ticket.winner_at = now
        return ticket
