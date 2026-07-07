from datetime import datetime

from pydantic import BaseModel

from app.modules.raffles.models import RaffleStatus


class RaffleCounts(BaseModel):
    total: int
    active: int  # draft + published (not closed/archived)
    draft: int
    published: int
    closed: int
    archived: int


class TicketCounts(BaseModel):
    total: int
    available: int
    reserved: int
    paid: int


class SalesSummary(BaseModel):
    """Monetary summary. No real payments yet — these are potential/derived
    values (ticket_price * counts), a clean seat for real revenue later."""

    potential_value: float
    reserved_value: float
    paid_value: float


class RecentReservation(BaseModel):
    number: int
    raffle_title: str
    participant_name: str | None
    reserved_at: datetime


class RecentRaffle(BaseModel):
    title: str
    status: RaffleStatus
    total_tickets: int
    available_count: int


class DashboardOverview(BaseModel):
    """Single aggregated payload for the whole dashboard (one request)."""

    raffles: RaffleCounts
    tickets: TicketCounts
    participants: int
    collaborators: int
    sales: SalesSummary
    recent_reservations: list[RecentReservation]
    recent_raffles: list[RecentRaffle]
