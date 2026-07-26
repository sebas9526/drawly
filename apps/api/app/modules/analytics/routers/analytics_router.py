"""Analytics & Reports endpoints (Sprint 9). Every route is owner-scoped via
`AnalyticsUseCasesDep` (see dependencies) and never returns another user's
data. See docs/04-api/API_SPECIFICATION.md ("Analytics") for the full filter
and export contract.
"""

import uuid
from datetime import date
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Query, Response

from app.core.pagination import build_pagination_meta, offset_for
from app.core.responses import PaginatedResponse, SuccessResponse
from app.modules.analytics.dependencies import AnalyticsUseCasesDep
from app.modules.analytics.schemas import (
    AnalyticsFilters,
    CollaboratorReportRow,
    ExecutiveDashboard,
    GlobalReports,
    ParticipantReportRow,
    RaffleReportDetail,
    RaffleReportRow,
)
from app.modules.analytics.services import build_excel, build_pdf
from app.modules.raffles.models import RaffleStatus
from app.modules.tickets.models import TicketStatus

router = APIRouter()

ExportFormat = Literal["excel", "pdf"]


def _filters(
    *,
    start_date: date | None,
    end_date: date | None,
    raffle_id: uuid.UUID | None,
    status: TicketStatus | None = None,
    collaborator_id: uuid.UUID | None,
) -> AnalyticsFilters:
    return AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        raffle_id=raffle_id,
        status=status,
        collaborator_id=collaborator_id,
    )


def _export_response(
    export_format: ExportFormat, title: str, headers: list[str], rows: list[list[Any]]
) -> Response:
    if export_format == "excel":
        content = build_excel(title=title, headers=headers, rows=rows)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{title}.xlsx"
    else:
        content = build_pdf(title=title, headers=headers, rows=rows)
        media_type = "application/pdf"
        filename = f"{title}.pdf"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ----------------------------------------------------------------------
# Executive dashboard
# ----------------------------------------------------------------------


@router.get("/dashboard", response_model=SuccessResponse[ExecutiveDashboard])
async def get_dashboard(
    use_cases: AnalyticsUseCasesDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    raffle_id: Annotated[uuid.UUID | None, Query()] = None,
    status: Annotated[TicketStatus | None, Query()] = None,
    collaborator_id: Annotated[uuid.UUID | None, Query()] = None,
) -> SuccessResponse[ExecutiveDashboard]:
    overview = await use_cases.get_dashboard(
        _filters(
            start_date=start_date,
            end_date=end_date,
            raffle_id=raffle_id,
            status=status,
            collaborator_id=collaborator_id,
        )
    )
    return SuccessResponse(message="Executive dashboard.", data=overview)


@router.get("/dashboard/export")
async def export_dashboard(
    use_cases: AnalyticsUseCasesDep,
    export_format: Annotated[ExportFormat, Query(alias="format")] = "excel",
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    raffle_id: Annotated[uuid.UUID | None, Query()] = None,
    status: Annotated[TicketStatus | None, Query()] = None,
    collaborator_id: Annotated[uuid.UUID | None, Query()] = None,
) -> Response:
    title, headers, rows = await use_cases.export_dashboard_rows(
        _filters(
            start_date=start_date,
            end_date=end_date,
            raffle_id=raffle_id,
            status=status,
            collaborator_id=collaborator_id,
        )
    )
    return _export_response(export_format, title, headers, rows)


# ----------------------------------------------------------------------
# Raffle report
# ----------------------------------------------------------------------


@router.get("/raffles", response_model=PaginatedResponse[RaffleReportRow])
async def list_raffles(
    use_cases: AnalyticsUseCasesDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    raffle_id: Annotated[uuid.UUID | None, Query()] = None,
    raffle_status: Annotated[RaffleStatus | None, Query()] = None,
    collaborator_id: Annotated[uuid.UUID | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[RaffleReportRow]:
    filters = _filters(
        start_date=start_date,
        end_date=end_date,
        raffle_id=raffle_id,
        collaborator_id=collaborator_id,
    )
    rows, total = await use_cases.list_raffles(
        filters,
        raffle_status=raffle_status,
        offset=offset_for(page, page_size),
        limit=page_size,
    )
    return PaginatedResponse(
        data=rows, pagination=build_pagination_meta(page=page, page_size=page_size, total=total)
    )


@router.get("/raffles/export")
async def export_raffles(
    use_cases: AnalyticsUseCasesDep,
    export_format: Annotated[ExportFormat, Query(alias="format")] = "excel",
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    raffle_id: Annotated[uuid.UUID | None, Query()] = None,
    raffle_status: Annotated[RaffleStatus | None, Query()] = None,
    collaborator_id: Annotated[uuid.UUID | None, Query()] = None,
) -> Response:
    filters = _filters(
        start_date=start_date,
        end_date=end_date,
        raffle_id=raffle_id,
        collaborator_id=collaborator_id,
    )
    title, headers, rows = await use_cases.export_raffles_rows(filters, raffle_status=raffle_status)
    return _export_response(export_format, title, headers, rows)


@router.get("/raffles/{raffle_id}", response_model=SuccessResponse[RaffleReportDetail])
async def get_raffle_detail(
    raffle_id: uuid.UUID, use_cases: AnalyticsUseCasesDep
) -> SuccessResponse[RaffleReportDetail]:
    detail = await use_cases.get_raffle_detail(raffle_id)
    return SuccessResponse(message="Raffle report.", data=detail)


# ----------------------------------------------------------------------
# Collaborator report
# ----------------------------------------------------------------------


@router.get("/collaborators", response_model=PaginatedResponse[CollaboratorReportRow])
async def list_collaborators(
    use_cases: AnalyticsUseCasesDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    raffle_id: Annotated[uuid.UUID | None, Query()] = None,
    collaborator_id: Annotated[uuid.UUID | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[CollaboratorReportRow]:
    filters = _filters(
        start_date=start_date,
        end_date=end_date,
        raffle_id=raffle_id,
        collaborator_id=collaborator_id,
    )
    rows, total = await use_cases.list_collaborators(
        filters, offset=offset_for(page, page_size), limit=page_size
    )
    return PaginatedResponse(
        data=rows, pagination=build_pagination_meta(page=page, page_size=page_size, total=total)
    )


@router.get("/collaborators/export")
async def export_collaborators(
    use_cases: AnalyticsUseCasesDep,
    export_format: Annotated[ExportFormat, Query(alias="format")] = "excel",
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    raffle_id: Annotated[uuid.UUID | None, Query()] = None,
    collaborator_id: Annotated[uuid.UUID | None, Query()] = None,
) -> Response:
    filters = _filters(
        start_date=start_date,
        end_date=end_date,
        raffle_id=raffle_id,
        collaborator_id=collaborator_id,
    )
    title, headers, rows = await use_cases.export_collaborators_rows(filters)
    return _export_response(export_format, title, headers, rows)


# ----------------------------------------------------------------------
# Participant report
# ----------------------------------------------------------------------


@router.get("/participants", response_model=PaginatedResponse[ParticipantReportRow])
async def list_participants(
    use_cases: AnalyticsUseCasesDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    raffle_id: Annotated[uuid.UUID | None, Query()] = None,
    collaborator_id: Annotated[uuid.UUID | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[ParticipantReportRow]:
    filters = _filters(
        start_date=start_date,
        end_date=end_date,
        raffle_id=raffle_id,
        collaborator_id=collaborator_id,
    )
    rows, total = await use_cases.list_participants(
        filters, offset=offset_for(page, page_size), limit=page_size
    )
    return PaginatedResponse(
        data=rows, pagination=build_pagination_meta(page=page, page_size=page_size, total=total)
    )


@router.get("/participants/export")
async def export_participants(
    use_cases: AnalyticsUseCasesDep,
    export_format: Annotated[ExportFormat, Query(alias="format")] = "excel",
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    raffle_id: Annotated[uuid.UUID | None, Query()] = None,
    collaborator_id: Annotated[uuid.UUID | None, Query()] = None,
) -> Response:
    filters = _filters(
        start_date=start_date,
        end_date=end_date,
        raffle_id=raffle_id,
        collaborator_id=collaborator_id,
    )
    title, headers, rows = await use_cases.export_participants_rows(filters)
    return _export_response(export_format, title, headers, rows)


# ----------------------------------------------------------------------
# Global reports (top rankings, time series, status distribution)
# ----------------------------------------------------------------------


@router.get("/sales", response_model=SuccessResponse[GlobalReports])
async def get_sales(
    use_cases: AnalyticsUseCasesDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    raffle_id: Annotated[uuid.UUID | None, Query()] = None,
    status: Annotated[TicketStatus | None, Query()] = None,
    collaborator_id: Annotated[uuid.UUID | None, Query()] = None,
) -> SuccessResponse[GlobalReports]:
    filters = _filters(
        start_date=start_date,
        end_date=end_date,
        raffle_id=raffle_id,
        status=status,
        collaborator_id=collaborator_id,
    )
    reports = await use_cases.get_global_reports(filters)
    return SuccessResponse(message="Global sales reports.", data=reports)
