import uuid
from datetime import datetime, timedelta
from typing import NamedTuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import utcnow
from app.modules.raffles.exceptions import (
    RaffleHasParticipantsError,
    RaffleNotFoundError,
    WinningTicketNotFoundError,
)
from app.modules.raffles.models import Raffle, RaffleStatus
from app.modules.raffles.repositories import RaffleRepository
from app.modules.raffles.schemas import RaffleCreate, RaffleUpdate
from app.modules.raffles.services import RaffleService, TicketProvisioning


class WinnerRegistrationResult(NamedTuple):
    valid: bool
    ticket_id: uuid.UUID
    participant_id: uuid.UUID | None
    winner_at: datetime | None


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
        """Permanent delete — the raffle row and every one of its tickets are
        actually removed, not soft-deleted (an explicit organizer decision:
        "Eliminar" should mean gone, everywhere). Still blocked once any of
        the raffle's tickets already has a participant assigned
        (docs/02-architecture/DOMAIN_MODEL.md) — real reservation/purchase
        history is exactly the case this guard exists to protect, now more
        than ever since there's no soft-delete safety net to recover from.
        collaborator_raffles links are cleaned up by the DB itself (ON DELETE
        CASCADE, migration 0012) — a pure join table, not a cross-module
        concern this use case needs to know about."""
        raffle = await self.get(raffle_id)
        if await self._tickets.count_with_participant_for_raffle(raffle.id) > 0:
            raise RaffleHasParticipantsError()
        if raffle.winner_ticket_id is not None:
            # Clear the raffle's own FK into tickets first — otherwise
            # hard-deleting its tickets next would violate that constraint.
            raffle.winner_ticket_id = None
            await self._repository.save(raffle)
        await self._tickets.hard_delete_all_for_raffle(raffle.id)
        await self._repository.hard_delete(raffle)
        await self._session.commit()

    async def publish(self, raffle_id: uuid.UUID) -> Raffle:
        """draft -> published. Requires generated tickets, and — if the raffle
        has a scheduled publish_at — requires that date to have arrived (a
        schedule is a hard gate against publishing early). Makes the raffle
        visible on the public portal."""
        raffle = await self.get(raffle_id)
        has_tickets = await self._tickets.count_for_raffle(raffle.id) > 0
        self._service.ensure_can_publish(raffle, has_tickets=has_tickets, now=utcnow())
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
        """Public lookup: a published raffle is visible, and stays visible
        once closed (read-only) so the winner announcement has somewhere to
        show. Draft/archived/missing is a 404 to avoid leaking drafts."""
        raffle = await self._repository.get_by_slug(slug)
        if raffle is None or raffle.status not in (RaffleStatus.PUBLISHED, RaffleStatus.CLOSED):
            raise RaffleNotFoundError()
        return raffle

    async def cleanup_closed_raffles(self, *, grace_hours: int) -> list[Raffle]:
        """System-wide sweep: permanently deletes every CLOSED raffle (and
        its tickets) once it's been closed for at least ``grace_hours`` —
        hard delete, same as the manual "Eliminar rifa" action, for one
        consistent meaning of "deleted" across the app. Not owner-scoped,
        same as publish_scheduled_raffles. Deliberately does NOT reuse
        RaffleUseCases.delete() — that blocks on any ticket with a
        participant, which is the expected, common case for a concluded
        raffle; this is automatic post-raffle cleanup, not an accidental
        delete to protect against. One commit per raffle rather than
        batching the whole sweep into a single transaction."""
        cutoff = utcnow() - timedelta(hours=grace_hours)
        candidates = await self._repository.list_closed_past_cutoff(cutoff=cutoff)
        cleaned: list[Raffle] = []
        for raffle in candidates:
            if raffle.winner_ticket_id is not None:
                raffle.winner_ticket_id = None
                await self._repository.save(raffle)
            await self._tickets.hard_delete_all_for_raffle(raffle.id)
            await self._repository.hard_delete(raffle)
            await self._session.commit()
            cleaned.append(raffle)
        return cleaned

    async def register_winner(
        self, raffle_id: uuid.UUID, ticket_number: int
    ) -> WinnerRegistrationResult:
        """Manual winner entry: looks up the ticket by number and, only if it
        is already PAID, confirms it as the winner and closes the raffle in
        one transaction. If it isn't paid, the attempt is still recorded
        (Raffle.winner_ticket_id) but nothing closes — the organizer can just
        try another number."""
        raffle = await self.get(raffle_id)
        self._service.ensure_open_for_winner(raffle)

        candidate = await self._tickets.find_winner_candidate(raffle.id, ticket_number)
        if candidate is None:
            raise WinningTicketNotFoundError()

        now = utcnow()
        if candidate.is_paid:
            await self._tickets.confirm_winner(candidate.ticket_id)
            self._service.close_with_winner(raffle, candidate.ticket_id, now)
        else:
            self._service.record_winner_attempt(raffle, candidate.ticket_id)

        await self._repository.save(raffle)
        await self._session.commit()
        return WinnerRegistrationResult(
            valid=candidate.is_paid,
            ticket_id=candidate.ticket_id,
            participant_id=candidate.participant_id,
            winner_at=now if candidate.is_paid else None,
        )

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
