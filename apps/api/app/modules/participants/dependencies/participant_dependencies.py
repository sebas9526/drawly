from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.participants.repositories import ParticipantRepository
from app.modules.participants.services import ParticipantTickets
from app.modules.participants.use_cases import ParticipantUseCases
from app.modules.tickets.dependencies import get_participant_tickets
from app.modules.users.dependencies import CurrentUserDep


def get_participant_use_cases(
    session: Annotated[AsyncSession, Depends(get_session)],
    tickets: Annotated[ParticipantTickets, Depends(get_participant_tickets)],
    current_user: CurrentUserDep,
) -> ParticipantUseCases:
    """Admin surface: authenticated and owner-scoped."""
    return ParticipantUseCases(
        session=session,
        repository=ParticipantRepository(session),
        tickets=tickets,
        owner_id=current_user.id,
    )


def get_public_participants(
    session: Annotated[AsyncSession, Depends(get_session)],
    tickets: Annotated[ParticipantTickets, Depends(get_participant_tickets)],
) -> ParticipantUseCases:
    """Exposes ParticipantUseCases as the public module's PublicParticipants
    port (find-or-create by phone). Unscoped: the raffle owner is supplied to
    find_or_create explicitly."""
    return ParticipantUseCases(
        session=session,
        repository=ParticipantRepository(session),
        tickets=tickets,
    )


ParticipantUseCasesDep = Annotated[ParticipantUseCases, Depends(get_participant_use_cases)]
