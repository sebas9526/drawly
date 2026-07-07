import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.participants.exceptions import (
    ParticipantHasTicketsError,
    ParticipantNotFoundError,
)
from app.modules.participants.models import Participant
from app.modules.participants.repositories import ParticipantRepository
from app.modules.participants.schemas import (
    ParticipantCreate,
    ParticipantRead,
    ParticipantUpdate,
)
from app.modules.participants.services import ParticipantService, ParticipantTickets
from app.modules.tickets.models import Ticket


class ParticipantUseCases:
    """Application layer: orchestrates repository + domain service + the tickets
    port, and owns the transaction boundary. Ticket counts/history come from the
    tickets module through the ``ParticipantTickets`` port (never a direct join)."""

    def __init__(
        self,
        session: AsyncSession,
        repository: ParticipantRepository,
        tickets: ParticipantTickets,
        service: ParticipantService | None = None,
        owner_id: uuid.UUID | None = None,
    ) -> None:
        self._session = session
        self._repository = repository
        self._tickets = tickets
        self._service = service or ParticipantService()
        # Owner bound at composition time. Set for the admin surface (scopes every
        # read/mutation to the caller); None for the public find-or-create port,
        # which receives the raffle owner explicitly.
        self._owner_id = owner_id

    async def create(self, data: ParticipantCreate) -> ParticipantRead:
        phone = ParticipantService.normalize_phone(data.phone)
        self._service.ensure_phone_available(
            phone_taken=await self._repository.phone_exists(phone, owner_id=self._owner_id)
        )
        participant = self._service.build_participant(data, owner_id=self._owner_id)
        created = await self._repository.add(participant)
        await self._session.commit()
        return ParticipantRead.from_entity(created, ticket_count=0)

    async def get(self, participant_id: uuid.UUID) -> ParticipantRead:
        participant = await self._require(participant_id)
        count = await self._tickets.count_by_participant(participant_id)
        return ParticipantRead.from_entity(participant, ticket_count=count)

    async def list_participants(
        self, *, search: str | None, offset: int, limit: int
    ) -> tuple[list[ParticipantRead], int]:
        participants, total = await self._repository.list_paginated(
            search=search, offset=offset, limit=limit, owner_id=self._owner_id
        )
        counts = await self._tickets.count_by_participants([p.id for p in participants])
        reads = [
            ParticipantRead.from_entity(p, ticket_count=counts.get(p.id, 0)) for p in participants
        ]
        return reads, total

    async def update(self, participant_id: uuid.UUID, data: ParticipantUpdate) -> ParticipantRead:
        participant = await self._require(participant_id)
        if data.phone is not None:
            phone = ParticipantService.normalize_phone(data.phone)
            self._service.ensure_phone_available(
                phone_taken=await self._repository.phone_exists(
                    phone, exclude_id=participant_id, owner_id=self._owner_id
                )
            )
        self._service.apply_update(participant, data)
        saved = await self._repository.save(participant)
        await self._session.commit()
        count = await self._tickets.count_by_participant(participant_id)
        return ParticipantRead.from_entity(saved, ticket_count=count)

    async def delete(self, participant_id: uuid.UUID) -> None:
        participant = await self._require(participant_id)
        if await self._tickets.count_by_participant(participant_id) > 0:
            raise ParticipantHasTicketsError()
        await self._repository.soft_delete(participant)
        await self._session.commit()

    async def get_tickets(self, participant_id: uuid.UUID) -> list[Ticket]:
        await self._require(participant_id)
        return await self._tickets.list_by_participant(participant_id)

    async def find_or_create(
        self, data: ParticipantCreate, owner_id: uuid.UUID | None = None
    ) -> Participant:
        """Reuse an existing participant matched by phone (never overwriting
        their data), otherwise create one. Used by the public reservation flow to
        avoid duplicates. ``owner_id`` is the raffle owner, so the participant is
        filed under the correct tenant."""
        phone = ParticipantService.normalize_phone(data.phone)
        existing = await self._repository.get_by_phone(phone, owner_id=owner_id)
        if existing is not None:
            return existing
        participant = self._service.build_participant(data, owner_id=owner_id)
        created = await self._repository.add(participant)
        await self._session.commit()
        return created

    async def _require(self, participant_id: uuid.UUID) -> Participant:
        participant = await self._repository.get(participant_id, owner_id=self._owner_id)
        if participant is None:
            raise ParticipantNotFoundError()
        return participant
