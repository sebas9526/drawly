import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import utcnow
from app.modules.raffles.exceptions import RaffleHasParticipantsError, RaffleNotFoundError
from app.modules.raffles.models import Raffle, RaffleStatus
from app.modules.raffles.repositories import RaffleRepository
from app.modules.raffles.schemas import RaffleCreate, RaffleUpdate
from app.modules.raffles.services import RaffleService, TicketProvisioning


class RaffleUseCases:
    """Application layer: orchestrates repository + domain service + the ticket
    provisioning port, and owns the transaction boundary (commit/rollback)."""

    def __init__(
        self,
        session: AsyncSession,
        repository: RaffleRepository,
        tickets: TicketProvisioning,
        service: RaffleService | None = None,
        owner_id: uuid.UUID | None = None,
    ) -> None:
        self._session = session
        self._repository = repository
        self._tickets = tickets
        self._service = service or RaffleService()
        # Owner bound at composition time. Set for the admin surface (scopes every
        # read/mutation to the caller); None for the public port (slug lookup).
        self._owner_id = owner_id

    async def create(self, data: RaffleCreate) -> Raffle:
        slug = await self._unique_slug(self._service.slug_candidate(data.title))
        raffle = self._service.build_raffle(data, slug, owner_id=self._owner_id)
        created = await self._repository.add(raffle)
        await self._session.commit()
        return created

    async def get(self, raffle_id: uuid.UUID) -> Raffle:
        raffle = await self._repository.get(raffle_id, owner_id=self._owner_id)
        if raffle is None:
            raise RaffleNotFoundError()
        return raffle

    async def list_raffles(self, *, offset: int, limit: int) -> tuple[list[Raffle], int]:
        return await self._repository.list_paginated(
            offset=offset, limit=limit, owner_id=self._owner_id
        )

    async def update(self, raffle_id: uuid.UUID, data: RaffleUpdate) -> Raffle:
        raffle = await self.get(raffle_id)
        self._service.apply_update(raffle, data)
        saved = await self._repository.save(raffle)
        await self._session.commit()
        return saved

    async def delete(self, raffle_id: uuid.UUID) -> None:
        """Soft delete. Blocked once any of the raffle's tickets already has a
        participant assigned (docs/02-architecture/DOMAIN_MODEL.md) — those
        tickets carry real reservation/purchase history that a delete would
        orphan."""
        raffle = await self.get(raffle_id)
        if await self._tickets.count_with_participant_for_raffle(raffle.id) > 0:
            raise RaffleHasParticipantsError()
        await self._repository.soft_delete(raffle)
        await self._session.commit()

    async def publish(self, raffle_id: uuid.UUID) -> Raffle:
        """draft -> published. Requires generated tickets. Makes the raffle
        visible on the public portal."""
        raffle = await self.get(raffle_id)
        has_tickets = await self._tickets.count_for_raffle(raffle.id) > 0
        self._service.ensure_can_publish(raffle, has_tickets=has_tickets)
        self._service.publish(raffle)
        saved = await self._repository.save(raffle)
        await self._session.commit()
        return saved

    async def publish_scheduled_raffles(self) -> list[Raffle]:
        """System-wide sweep: auto-publishes every DRAFT raffle whose
        ``publish_at`` has arrived AND that already has generated tickets —
        the same precondition as a manual publish (RaffleService.
        ensure_can_publish). A raffle whose schedule arrives before tickets
        exist is left alone and retried on the next tick rather than skipped
        forever. Called periodically by the in-process scheduler (see
        app/modules/raffles/dependencies); not owner-scoped."""
        now = utcnow()
        candidates = await self._repository.list_scheduled_to_publish(now=now)
        published: list[Raffle] = []
        for raffle in candidates:
            has_tickets = await self._tickets.count_for_raffle(raffle.id) > 0
            if not has_tickets:
                continue
            self._service.publish(raffle)
            published.append(await self._repository.save(raffle))
        if published:
            await self._session.commit()
        return published

    async def get_published_by_slug(self, slug: str) -> Raffle:
        """Public lookup: only a published raffle is visible. Anything else
        (draft, closed, archived, missing) is a 404 to avoid leaking drafts."""
        raffle = await self._repository.get_by_slug(slug)
        if raffle is None or raffle.status is not RaffleStatus.PUBLISHED:
            raise RaffleNotFoundError()
        return raffle

    async def generate_tickets(self, raffle_id: uuid.UUID) -> int:
        """Explicit, idempotency-guarded generation (separate from raffle
        creation by design — enables reconfiguring numbering before publishing).
        The tickets module enforces 'generate only once' via its own conflict."""
        raffle = await self.get(raffle_id)
        self._service.ensure_editable(raffle)
        generated = await self._tickets.generate_for_raffle(
            raffle.id,
            raffle.total_tickets,
            raffle.owner_id,
            starting_number=raffle.starting_number,
        )
        return generated

    async def _unique_slug(self, base: str) -> str:
        candidate = base
        suffix = 2
        while await self._repository.exists_slug(candidate):
            candidate = f"{base}-{suffix}"
            suffix += 1
        return candidate
