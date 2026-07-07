import type {
  AnalyticsFiltersQuery,
  AnalyticsRafflesQuery,
  RaffleStatus,
  TicketStatus,
} from '@drawly/api-client';

/** UI-friendly (camelCase, always-string) filter state. Converted to the
 * snake_case query shape the API expects at the point of each request. */
export interface ReportFilterValues {
  startDate: string;
  endDate: string;
  raffleId: string;
  raffleStatus: string;
  status: string;
  collaboratorId: string;
}

export const EMPTY_REPORT_FILTERS: ReportFilterValues = {
  startDate: '',
  endDate: '',
  raffleId: '',
  raffleStatus: '',
  status: '',
  collaboratorId: '',
};

export function toAnalyticsFilters(values: ReportFilterValues): AnalyticsFiltersQuery {
  return {
    start_date: values.startDate || undefined,
    end_date: values.endDate || undefined,
    raffle_id: values.raffleId || undefined,
    status: (values.status || undefined) as TicketStatus | undefined,
    collaborator_id: values.collaboratorId || undefined,
  };
}

export function toAnalyticsRafflesFilters(values: ReportFilterValues): AnalyticsRafflesQuery {
  return {
    ...toAnalyticsFilters(values),
    raffle_status: (values.raffleStatus || undefined) as RaffleStatus | undefined,
  };
}
