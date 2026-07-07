import uuid
from decimal import Decimal

from app.modules.raffles.exceptions import RaffleNotEditableError, RaffleNotPublishableError
from app.modules.raffles.models import Raffle, RaffleStatus
from app.modules.raffles.schemas import RaffleCreate, RaffleUpdate
from app.modules.raffles.validators import slugify


class RaffleService:
    """Pure raffle domain rules. No I/O, so it is unit-testable without a DB."""

    @staticmethod
    def build_raffle(
        data: RaffleCreate, public_slug: str, owner_id: uuid.UUID | None = None
    ) -> Raffle:
        return Raffle(
            owner_id=owner_id,
            title=data.title,
            description=data.description,
            prize=data.prize,
            ticket_price=data.ticket_price,
            total_tickets=data.total_tickets,
            draw_date=data.draw_date,
            status=RaffleStatus.DRAFT,
            public_slug=public_slug,
        )

    @staticmethod
    def slug_candidate(title: str) -> str:
        base = slugify(title)
        return base or "raffle"

    @staticmethod
    def ensure_editable(raffle: Raffle) -> None:
        """A raffle may only change while still in draft."""
        if raffle.status is not RaffleStatus.DRAFT:
            raise RaffleNotEditableError()

    @staticmethod
    def ensure_can_publish(raffle: Raffle, *, has_tickets: bool) -> None:
        """A raffle is publishable only from draft and once it has tickets
        (docs/02-architecture/DOMAIN_MODEL.md). The ticket-count check is passed
        in so this rule stays pure/testable."""
        if raffle.status is not RaffleStatus.DRAFT:
            raise RaffleNotPublishableError("Only a draft raffle can be published.")
        if not has_tickets:
            raise RaffleNotPublishableError("Generate tickets before publishing the raffle.")

    @staticmethod
    def publish(raffle: Raffle) -> Raffle:
        raffle.status = RaffleStatus.PUBLISHED
        return raffle

    @classmethod
    def apply_update(cls, raffle: Raffle, data: RaffleUpdate) -> Raffle:
        cls.ensure_editable(raffle)
        if data.title is not None:
            raffle.title = data.title
        if data.description is not None:
            raffle.description = data.description
        if data.prize is not None:
            raffle.prize = data.prize
        if data.ticket_price is not None:
            raffle.ticket_price = Decimal(data.ticket_price)
        if data.total_tickets is not None:
            raffle.total_tickets = data.total_tickets
        if data.draw_date is not None:
            raffle.draw_date = data.draw_date
        return raffle
