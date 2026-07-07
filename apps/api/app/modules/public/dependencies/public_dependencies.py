from typing import Annotated

from fastapi import Depends

from app.modules.collaborators.dependencies import get_public_collaborators
from app.modules.participants.dependencies import get_public_participants
from app.modules.public.services import (
    PublicCollaborators,
    PublicParticipants,
    PublicRaffles,
    PublicTickets,
)
from app.modules.public.use_cases import PublicRaffleUseCases
from app.modules.raffles.dependencies import get_public_raffles
from app.modules.tickets.dependencies import get_public_tickets


def get_public_use_cases(
    raffles: Annotated[PublicRaffles, Depends(get_public_raffles)],
    tickets: Annotated[PublicTickets, Depends(get_public_tickets)],
    participants: Annotated[PublicParticipants, Depends(get_public_participants)],
    collaborators: Annotated[PublicCollaborators, Depends(get_public_collaborators)],
) -> PublicRaffleUseCases:
    # All providers depend on the same request-scoped DB session, so the
    # reservation runs on one connection.
    return PublicRaffleUseCases(
        raffles=raffles,
        tickets=tickets,
        participants=participants,
        collaborators=collaborators,
    )


PublicUseCasesDep = Annotated[PublicRaffleUseCases, Depends(get_public_use_cases)]
