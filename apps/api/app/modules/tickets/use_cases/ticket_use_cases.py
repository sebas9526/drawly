import uuid
from collections.abc import Sequence
from datetime import timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.base import utcnow
from app.modules.tickets.exceptions import (
    CollaboratorNotFoundForTicketError,
    ParticipantNotFoundForTicketError,
    TicketNotFoundError,
    TicketsAlreadyGeneratedError,
)
from app.modules.tickets.models import Ticket, TicketStatus
from app.modules.tickets.repositories import TicketRepository
from app.modules.tickets.services import (
    TicketCollaborators,
    TicketGenerationService,
    TicketService,
)


class TicketUseCases:
    """Application layer for tickets. Owns transactions and loads/persists
    entities; all transition *rules* are delegated to ``TicketService``.

    Structurally implements two ports (Dependency Inversion, so neither the
    raffles nor participants module imports this class directly):
    - raffles' ``TicketProvisioning`` via ``generate_for_raffle``;
    - participants' ``ParticipantTickets`` via the ``*_by_participant`` reads.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: TicketRepository,
        service: TicketService | None = None,
        generator: TicketGenerationService | None = None,
        owner_id: uuid.UUID | None = None,
        collaborators: TicketCollaborators | None = None,
    ) -> None:
        self._session = session
        self._repository = repository
        self._service = service or TicketService()
        self._generator = generator or TicketGenerationService()
        # Owner bound at composition time. Set for the admin surface (scopes every
        # read/mutation to the caller); None for the internal ports (raffles
        # provisioning, participants reads, public reserve) which scope otherwise.
        self._owner_id = owner_id
        # Collaborator validation port (admin + public reservation). When None,
        # collaborator crediting is skipped (e.g. raffle provisioning).
        self._collaborators = collaborators

    @property
    def _ttl(self) -> timedelta:
        return timedelta(hours=get_settings().reservation_ttl_hours)

    async def release_expired_reservations(self) -> list[Ticket]:
        """System-wide sweep: releases every RESERVED ticket whose TTL has
        elapsed back to AVAILABLE, across all owners. Called periodically by
        the in-process scheduler (see app/modules/tickets/jobs); not owner
        scoped since expiry isn't a per-request, per-owner concern."""
        now = utcnow()
        expired = await self._repository.list_expired_reserved(now=now)
        released: list[Ticket] = []
        for ticket in expired:
            self._service.release_expired(ticket, now=now)
            released.append(await self._repository.save(ticket))
        if released:
            await self._session.commit()
        return released

    async def generate_for_raffle(
        self,
        raffle_id: uuid.UUID,
        quantity: int,
        owner_id: uuid.UUID | None = None,
        starting_number: int = 1,
    ) -> int:
        if await self._repository.count_by_raffle(raffle_id) > 0:
            raise TicketsAlreadyGeneratedError()
        tickets = self._generator.generate(
            raffle_id,
            quantity,
            now=utcnow(),
            owner_id=owner_id,
            starting_number=starting_number,
        )
        created = await self._repository.add_all(tickets)
        await self._session.commit()
        return created

    async def list_tickets(
        self,
        *,
        raffle_id: uuid.UUID | None,
        status: TicketStatus | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Ticket], int]:
        return await self._repository.list_paginated(
            raffle_id=raffle_id,
            status=status,
            offset=offset,
            limit=limit,
            owner_id=self._owner_id,
        )

    async def list_available(self, raffle_id: uuid.UUID) -> list[Ticket]:
        return await self._repository.list_available(raffle_id, owner_id=self._owner_id)

    async def get_ticket(self, ticket_id: uuid.UUID) -> Ticket:
        ticket = await self._repository.get(ticket_id, owner_id=self._owner_id)
        if ticket is None:
            raise TicketNotFoundError()
        return ticket

    async def reserve_ticket(
        self,
        ticket_id: uuid.UUID,
        participant_id: uuid.UUID | None,
        collaborator_id: uuid.UUID | None = None,
    ) -> Ticket:
        # Row lock so concurrent reservers can't both grab the same ticket.
        ticket = await self._repository.get_for_update(ticket_id, owner_id=self._owner_id)
        if ticket is None:
            raise TicketNotFoundError()
        await self._validate_collaborator(collaborator_id, ticket.raffle_id)
        self._service.reserve(
            ticket,
            now=utcnow(),
            ttl=self._ttl,
            participant_id=participant_id,
            collaborator_id=collaborator_id,
        )
        saved = await self._repository.save(ticket)
        await self._session.commit()
        return saved

    async def set_collaborator(
        self, ticket_id: uuid.UUID, collaborator_id: uuid.UUID | None
    ) -> Ticket:
        """Admin: credit or clear the collaborator (seller) on a reserved ticket."""
        ticket = await self.get_ticket(ticket_id)
        await self._validate_collaborator(collaborator_id, ticket.raffle_id)
        self._service.set_collaborator(ticket, collaborator_id=collaborator_id)
        saved = await self._repository.save(ticket)
        await self._session.commit()
        return saved

    async def _validate_collaborator(
        self, collaborator_id: uuid.UUID | None, raffle_id: uuid.UUID
    ) -> None:
        """Ensure the collaborator belongs to the ticket's raffle (and owner when
        admin / is active when public). No-op when no collaborator or no port."""
        if collaborator_id is None or self._collaborators is None:
            return
        # Admin path (owner set): scope to owner, allow inactive. Public path
        # (owner None): require the collaborator to be active.
        ok = await self._collaborators.exists_in_raffle(
            collaborator_id,
            raffle_id,
            owner_id=self._owner_id,
            active_only=self._owner_id is None,
        )
        if not ok:
            raise CollaboratorNotFoundForTicketError()

    async def cancel_reservation(self, ticket_id: uuid.UUID) -> Ticket:
        ticket = await self.get_ticket(ticket_id)
        self._service.cancel_reservation(ticket, now=utcnow())
        saved = await self._repository.save(ticket)
        await self._session.commit()
        return saved

    async def mark_as_paid(self, ticket_id: uuid.UUID) -> Ticket:
        ticket = await self.get_ticket(ticket_id)
        self._service.mark_as_paid(ticket, now=utcnow())
        saved = await self._repository.save(ticket)
        await self._session.commit()
        return saved

    async def assign_participant(self, ticket_id: uuid.UUID, participant_id: uuid.UUID) -> Ticket:
        ticket = await self.get_ticket(ticket_id)
        self._service.assign_participant(
            ticket, participant_id=participant_id, now=utcnow(), ttl=self._ttl
        )
        try:
            saved = await self._repository.save(ticket)
            await self._session.commit()
        except IntegrityError as error:
            await self._session.rollback()
            # participant_id has a FK to participants; a violation means the
            # participant does not exist. Surface a clean 404 without importing
            # the participants module.
            raise ParticipantNotFoundForTicketError() from error
        return saved

    async def unassign_participant(self, ticket_id: uuid.UUID) -> Ticket:
        ticket = await self.get_ticket(ticket_id)
        self._service.unassign_participant(ticket, now=utcnow())
        saved = await self._repository.save(ticket)
        await self._session.commit()
        return saved

    # --- ParticipantTickets port (consumed by the participants module) ---

    async def count_by_participant(self, participant_id: uuid.UUID) -> int:
        return await self._repository.count_by_participant(participant_id)

    async def count_by_participants(
        self, participant_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, int]:
        return await self._repository.count_by_participants(participant_ids)

    async def list_by_participant(self, participant_id: uuid.UUID) -> list[Ticket]:
        return await self._repository.list_by_participant(participant_id)

    # --- raffles TicketProvisioning port (count) + public reads ---

    async def count_for_raffle(self, raffle_id: uuid.UUID) -> int:
        return await self._repository.count_by_raffle(raffle_id)

    async def count_with_participant_for_raffle(self, raffle_id: uuid.UUID) -> int:
        return await self._repository.count_with_participant_by_raffle(raffle_id)

    async def status_counts(self, raffle_id: uuid.UUID) -> dict[TicketStatus, int]:
        return await self._repository.status_counts(raffle_id)

    async def list_by_raffle(
        self, raffle_id: uuid.UUID, *, offset: int, limit: int
    ) -> tuple[list[Ticket], int]:
        return await self._repository.list_by_raffle(raffle_id, offset=offset, limit=limit)

    async def get_by_number(self, raffle_id: uuid.UUID, number: int) -> Ticket | None:
        return await self._repository.get_by_raffle_and_number(raffle_id, number)
