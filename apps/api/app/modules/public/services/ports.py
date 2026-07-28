"""Ports the public portal depends on. Dependency Inversion keeps the public
module decoupled from the admin modules' internals: raffles/tickets/participants
use cases satisfy these structurally, wired only in public/dependencies. The
public module is a read/orchestration layer — it holds no tables and reuses the
existing domain logic (no admin endpoints are reused)."""

import uuid
from typing import Protocol

from app.modules.collaborators.models import Collaborator
from app.modules.participants.models import Participant
from app.modules.participants.schemas import ParticipantCreate, ParticipantRead
from app.modules.raffles.models import Raffle
from app.modules.tickets.models import Ticket, TicketStatus


class PublicRaffles(Protocol):
    async def get_published_by_slug(self, slug: str) -> Raffle: ...


class PublicTickets(Protocol):
    async def status_counts(self, raffle_id: uuid.UUID) -> dict[TicketStatus, int]: ...

    async def list_by_raffle(
        self, raffle_id: uuid.UUID, *, offset: int, limit: int
    ) -> tuple[list[Ticket], int]: ...

    async def get_by_number(self, raffle_id: uuid.UUID, number: int) -> Ticket | None: ...

    async def get_by_id(self, ticket_id: uuid.UUID) -> Ticket | None: ...

    async def reserve_ticket(
        self,
        ticket_id: uuid.UUID,
        participant_id: uuid.UUID | None,
        collaborator_id: uuid.UUID | None = None,
    ) -> Ticket: ...


class PublicParticipants(Protocol):
    async def find_or_create(
        self, data: ParticipantCreate, owner_id: uuid.UUID | None = None
    ) -> Participant: ...

    async def get(self, participant_id: uuid.UUID) -> ParticipantRead: ...


class PublicCollaborators(Protocol):
    async def list_by_raffle(
        self, raffle_id: uuid.UUID, *, active_only: bool = False
    ) -> list[Collaborator]: ...

    async def list_published_raffles(self, collaborator_id: uuid.UUID) -> list[Raffle] | None:
        """None if the collaborator doesn't exist, is inactive, or is
        deleted; otherwise their published raffles (possibly empty) — for the
        personal referral link (GET /public/collaborators/{id}/raffles)."""
        ...
