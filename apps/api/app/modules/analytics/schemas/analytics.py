"""Response DTOs for the analytics module. Plain ``pydantic.BaseModel`` (not
SQLModel) — these are read-only projections, never persisted."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.modules.raffles.models import RaffleStatus


class ExecutiveDashboard(BaseModel):
    """Top-level KPIs (Sprint 9). Independent from the Sprint-7 operational
    dashboard (`app.modules.dashboard`) — this module runs its own queries."""

    raffles_total: int
    raffles_published: int
    raffles_closed: int
    tickets_available: int
    tickets_reserved: int
    tickets_paid: int
    participants_total: int
    collaborators_total: int
    # "Ingresos esperados": sum(total_tickets * ticket_price) across matched raffles.
    expected_revenue: float
    # "Ingresos recibidos": sum(ticket_price) for PAID tickets. Derived from
    # ticket status, not a real transaction — the seat reserved for the future
    # Payments module (see docs/06-roadmap/ROADMAP.md).
    received_revenue: float
    percent_sold: float
    percent_reserved: float


class RankingEntry(BaseModel):
    """One row of a Top-N ranking (collaborator, raffle, or participant)."""

    id: uuid.UUID
    name: str
    count: int
    value: float
    rank: int


class RaffleReportRow(BaseModel):
    id: uuid.UUID
    title: str
    status: RaffleStatus
    created_at: datetime
    draw_date: datetime
    total_tickets: int
    available: int
    reserved: int
    paid: int
    percent_sold: float
    expected_revenue: float


class RaffleReportDetail(RaffleReportRow):
    """Single-raffle report, including the two rankings — only computed for one
    raffle at a time (never per-row in the list) to avoid N+1 queries."""

    top_collaborators: list[RankingEntry]
    top_participants: list[RankingEntry]


class CollaboratorReportRow(BaseModel):
    id: uuid.UUID
    name: str
    raffle_id: uuid.UUID
    raffle_title: str
    total_sales: int
    total_reservations: int
    participants_served: int
    expected_amount: float
    participation_percent: float
    rank: int


class ParticipantReportRow(BaseModel):
    id: uuid.UUID
    full_name: str
    purchases_count: int
    tickets_count: int
    amount_invested: float
    last_purchase_at: datetime | None
    raffles_count: int


class TimeSeriesPoint(BaseModel):
    day: date
    count: int
    value: float


class TicketStatusDistribution(BaseModel):
    available: int
    reserved: int
    paid: int
    cancelled: int
    winner: int


class GlobalReports(BaseModel):
    top_collaborators: list[RankingEntry]
    top_raffles: list[RankingEntry]
    top_participants: list[RankingEntry]
    sales_by_day: list[TimeSeriesPoint]
    reservations_by_day: list[TimeSeriesPoint]
    status_distribution: TicketStatusDistribution
