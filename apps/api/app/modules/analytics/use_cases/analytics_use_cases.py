"""Application layer: fetches aggregates via the repository and assembles the
response via the service. Every query is scoped to the authenticated owner."""

import uuid
from typing import Any

from app.core.exceptions import NotFoundError
from app.modules.analytics.repositories import AnalyticsRepository
from app.modules.analytics.schemas import (
    AnalyticsFilters,
    CollaboratorReportRow,
    ExecutiveDashboard,
    GlobalReports,
    ParticipantReportRow,
    RaffleReportDetail,
    RaffleReportRow,
    TimeSeriesPoint,
)
from app.modules.analytics.services import AnalyticsService
from app.modules.raffles.models import RaffleStatus

_RAFFLE_RANKING_LIMIT = 5
_GLOBAL_RANKING_LIMIT = 10

# Spanish column labels for exports, keyed by the underlying schema field name.
_EXPORT_LABELS: dict[str, str] = {
    "raffles_total": "Rifas totales",
    "raffles_published": "Rifas publicadas",
    "raffles_closed": "Rifas finalizadas",
    "tickets_available": "Boletas disponibles",
    "tickets_reserved": "Boletas reservadas",
    "tickets_paid": "Boletas pagadas",
    "participants_total": "Participantes",
    "collaborators_total": "Colaboradores",
    "expected_revenue": "Ingresos esperados",
    "received_revenue": "Ingresos recibidos",
    "percent_sold": "% vendido",
    "percent_reserved": "% reservado",
    "title": "Rifa",
    "status": "Estado",
    "created_at": "Creada",
    "draw_date": "Fecha de sorteo",
    "total_tickets": "Boletas",
    "available": "Disponibles",
    "reserved": "Reservadas",
    "paid": "Pagadas",
    "rank": "Ranking",
    "name": "Colaborador",
    "raffle_title": "Rifa",
    "total_sales": "Ventas",
    "total_reservations": "Reservas",
    "participants_served": "Participantes atendidos",
    "expected_amount": "Monto esperado",
    "participation_percent": "% participación",
    "full_name": "Participante",
    "purchases_count": "Compras",
    "tickets_count": "Boletas",
    "amount_invested": "Monto invertido",
    "last_purchase_at": "Última compra",
    "raffles_count": "Rifas",
}


def _labeled(field_keys: list[str]) -> list[str]:
    return [_EXPORT_LABELS.get(key, key) for key in field_keys]


class AnalyticsUseCases:
    def __init__(
        self,
        repository: AnalyticsRepository,
        owner_id: uuid.UUID,
        service: AnalyticsService | None = None,
    ) -> None:
        self._repository = repository
        self._owner_id = owner_id
        self._service = service or AnalyticsService()

    async def get_dashboard(self, filters: AnalyticsFilters) -> ExecutiveDashboard:
        raffle_aggregates = await self._repository.raffle_aggregates(self._owner_id, filters)
        ticket_aggregates = await self._repository.ticket_aggregates(self._owner_id, filters)
        participants_total = await self._repository.count_participants(self._owner_id)
        collaborators_total = await self._repository.count_collaborators(self._owner_id)
        return self._service.executive_dashboard(
            raffle_aggregates, ticket_aggregates, participants_total, collaborators_total
        )

    async def list_raffles(
        self,
        filters: AnalyticsFilters,
        *,
        raffle_status: RaffleStatus | None,
        offset: int,
        limit: int,
    ) -> tuple[list[RaffleReportRow], int]:
        rows, total = await self._repository.raffles_report_rows(
            self._owner_id, filters, raffle_status=raffle_status, offset=offset, limit=limit
        )
        return [self._service.raffle_report_row(row) for row in rows], total

    async def get_raffle_detail(self, raffle_id: uuid.UUID) -> RaffleReportDetail:
        rows, _total = await self._repository.raffles_report_rows(
            self._owner_id,
            AnalyticsFilters(raffle_id=raffle_id),
            raffle_status=None,
            offset=0,
            limit=1,
        )
        if not rows:
            raise NotFoundError("Raffle not found.")
        base = self._service.raffle_report_row(rows[0])
        top_collaborators = await self._repository.raffle_top_collaborators(
            raffle_id, self._owner_id, _RAFFLE_RANKING_LIMIT
        )
        top_participants = await self._repository.raffle_top_participants(
            raffle_id, self._owner_id, _RAFFLE_RANKING_LIMIT
        )
        return RaffleReportDetail(
            **base.model_dump(),
            top_collaborators=self._service.ranking(top_collaborators),
            top_participants=self._service.ranking(top_participants),
        )

    async def _all_collaborator_rows(
        self, filters: AnalyticsFilters
    ) -> list[CollaboratorReportRow]:
        """Full, ranked collaborator report — rank depends on the complete
        ordered set, so it must be computed before any pagination slice."""
        rows = await self._repository.collaborators_report_rows(self._owner_id, filters)
        served = await self._repository.participants_served_by_collaborator(self._owner_id, filters)
        raffle_ids = {row[2] for row in rows}
        raffle_totals = await self._repository.raffle_total_tickets(self._owner_id, raffle_ids)
        return self._service.collaborator_report_rows(rows, served, raffle_totals)

    async def list_collaborators(
        self, filters: AnalyticsFilters, *, offset: int, limit: int
    ) -> tuple[list[CollaboratorReportRow], int]:
        all_rows = await self._all_collaborator_rows(filters)
        return all_rows[offset : offset + limit], len(all_rows)

    async def _all_participant_rows(self, filters: AnalyticsFilters) -> list[ParticipantReportRow]:
        rows = await self._repository.participants_report_rows(self._owner_id, filters)
        raffles_count = await self._repository.raffles_count_by_participant(self._owner_id, filters)
        return self._service.participant_report_rows(rows, raffles_count)

    async def list_participants(
        self, filters: AnalyticsFilters, *, offset: int, limit: int
    ) -> tuple[list[ParticipantReportRow], int]:
        all_rows = await self._all_participant_rows(filters)
        return all_rows[offset : offset + limit], len(all_rows)

    async def get_global_reports(self, filters: AnalyticsFilters) -> GlobalReports:
        top_collaborators = await self._repository.top_collaborators_global(
            self._owner_id, filters, _GLOBAL_RANKING_LIMIT
        )
        top_raffles = await self._repository.top_raffles_global(
            self._owner_id, filters, _GLOBAL_RANKING_LIMIT
        )
        top_participants = await self._repository.top_participants_global(
            self._owner_id, filters, _GLOBAL_RANKING_LIMIT
        )
        sales_by_day = await self._repository.sales_by_day(self._owner_id, filters)
        reservations_by_day = await self._repository.reservations_by_day(self._owner_id, filters)
        status_counts = await self._repository.status_distribution(self._owner_id, filters)

        return GlobalReports(
            top_collaborators=self._service.ranking(top_collaborators),
            top_raffles=self._service.ranking(top_raffles),
            top_participants=self._service.ranking(top_participants),
            sales_by_day=[
                TimeSeriesPoint(day=day, count=count, value=value)
                for day, count, value in sales_by_day
            ],
            reservations_by_day=[
                TimeSeriesPoint(day=day, count=count, value=0.0)
                for day, count in reservations_by_day
            ],
            status_distribution=self._service.status_distribution(status_counts),
        )

    # ------------------------------------------------------------------
    # Export row-shaping (reuses the methods above — no separate query path).
    # Returns (title, headers, rows) consumed by export_service.build_excel/pdf.
    # ------------------------------------------------------------------

    async def export_dashboard_rows(
        self, filters: AnalyticsFilters
    ) -> tuple[str, list[str], list[list[Any]]]:
        overview = await self.get_dashboard(filters)
        field_keys = list(ExecutiveDashboard.model_fields.keys())
        return (
            "Dashboard ejecutivo",
            _labeled(field_keys),
            [[getattr(overview, key) for key in field_keys]],
        )

    async def export_raffles_rows(
        self, filters: AnalyticsFilters, *, raffle_status: RaffleStatus | None
    ) -> tuple[str, list[str], list[list[Any]]]:
        rows, _total = await self.list_raffles(
            filters, raffle_status=raffle_status, offset=0, limit=1000
        )
        field_keys = [
            "title",
            "status",
            "created_at",
            "draw_date",
            "total_tickets",
            "available",
            "reserved",
            "paid",
            "percent_sold",
            "expected_revenue",
        ]
        return (
            "Reporte de rifas",
            _labeled(field_keys),
            [[getattr(row, key) for key in field_keys] for row in rows],
        )

    async def export_collaborators_rows(
        self, filters: AnalyticsFilters
    ) -> tuple[str, list[str], list[list[Any]]]:
        rows = await self._all_collaborator_rows(filters)
        field_keys = [
            "rank",
            "name",
            "raffle_title",
            "total_sales",
            "total_reservations",
            "participants_served",
            "expected_amount",
            "participation_percent",
        ]
        return (
            "Reporte de colaboradores",
            _labeled(field_keys),
            [[getattr(row, key) for key in field_keys] for row in rows],
        )

    async def export_participants_rows(
        self, filters: AnalyticsFilters
    ) -> tuple[str, list[str], list[list[Any]]]:
        rows = await self._all_participant_rows(filters)
        field_keys = [
            "full_name",
            "purchases_count",
            "tickets_count",
            "amount_invested",
            "last_purchase_at",
            "raffles_count",
        ]
        return (
            "Reporte de participantes",
            _labeled(field_keys),
            [[getattr(row, key) for key in field_keys] for row in rows],
        )
