"""Shared query filters accepted by every analytics endpoint.

Not a request/response body — routers build this from individual ``Query()``
params (see docs/04-api/API_SPECIFICATION.md, "Analytics") and pass it straight
through use cases into the repository, which applies each field as an optional
``WHERE`` clause. Date range filters ``Ticket.reserved_at`` (every reserved/
paid/winner ticket has it set, so one column covers both reservation and sale
aggregates); the dedicated "sales per day" series additionally filters on
``Ticket.sold_at`` — see ``AnalyticsRepository.sales_by_day``.
"""

import uuid
from dataclasses import dataclass
from datetime import date

from app.modules.tickets.models import TicketStatus


@dataclass(frozen=True)
class AnalyticsFilters:
    start_date: date | None = None
    end_date: date | None = None
    raffle_id: uuid.UUID | None = None
    status: TicketStatus | None = None
    collaborator_id: uuid.UUID | None = None
