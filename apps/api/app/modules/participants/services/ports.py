import uuid
from collections.abc import Sequence
from typing import Protocol

from app.modules.tickets.models import Ticket


class ParticipantTickets(Protocol):
    """Port the participants module uses to read a participant's tickets.

    Dependency Inversion: participants depends on this abstraction; the tickets
    module's use case satisfies it, wired in participants/dependencies. Keeps the
    coupling one-directional (participants -> tickets) and acyclic — tickets does
    not import participants (ticket→participant integrity is enforced by the DB FK).
    """

    async def count_by_participant(self, participant_id: uuid.UUID) -> int: ...

    async def count_by_participants(
        self, participant_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, int]: ...

    async def list_by_participant(self, participant_id: uuid.UUID) -> list[Ticket]: ...

    async def numbers_by_participants(
        self, participant_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, list[int]]: ...

    async def collaborator_ids_by_participants(
        self, participant_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, list[uuid.UUID]]: ...


class ParticipantCollaborators(Protocol):
    """Port the participants module uses to resolve collaborator (seller)
    names — the tickets module knows collaborator_ids, but not names, which
    belong to the collaborators module. Coupling stays one-directional
    (participants -> collaborators); collaborators does not import
    participants."""

    async def names_by_ids(self, collaborator_ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, str]: ...
