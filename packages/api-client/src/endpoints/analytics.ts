import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient, PaginatedResult } from '../client/fetcher';
import type {
  AnalyticsExportFormat,
  AnalyticsFiltersQuery,
  AnalyticsRafflesQuery,
  CollaboratorReportRow,
  ExecutiveDashboard,
  GlobalReports,
  ParticipantReportRow,
  RaffleReportDetail,
  RaffleReportRow,
} from '../dto/analytics';

const BASE_PATH = `${API_V1_PREFIX}/analytics`;

/**
 * Analytics & Reports endpoints (Sprint 9). Every report reads from the
 * backend's own aggregation queries — the frontend never recomputes stats.
 * See docs/04-api/API_SPECIFICATION.md ("Analytics").
 */
export function createAnalyticsEndpoints(client: ApiClient) {
  return {
    getDashboard: (query?: AnalyticsFiltersQuery): Promise<ExecutiveDashboard> =>
      client.get<ExecutiveDashboard>(`${BASE_PATH}/dashboard`, { query }),

    getRaffles: (query?: AnalyticsRafflesQuery): Promise<PaginatedResult<RaffleReportRow>> =>
      client.getPaginated<RaffleReportRow>(`${BASE_PATH}/raffles`, { query }),

    getRaffleDetail: (raffleId: string): Promise<RaffleReportDetail> =>
      client.get<RaffleReportDetail>(`${BASE_PATH}/raffles/${raffleId}`),

    getCollaborators: (query?: AnalyticsFiltersQuery): Promise<CollaboratorReportRow[]> =>
      client.get<CollaboratorReportRow[]>(`${BASE_PATH}/collaborators`, { query }),

    getParticipants: (query?: AnalyticsFiltersQuery): Promise<ParticipantReportRow[]> =>
      client.get<ParticipantReportRow[]>(`${BASE_PATH}/participants`, { query }),

    getSales: (query?: AnalyticsFiltersQuery): Promise<GlobalReports> =>
      client.get<GlobalReports>(`${BASE_PATH}/sales`, { query }),

    exportDashboard: (
      format: AnalyticsExportFormat,
      query?: AnalyticsFiltersQuery,
    ): Promise<Blob> =>
      client.getBlob(`${BASE_PATH}/dashboard/export`, { query: { ...query, format } }),

    exportRaffles: (format: AnalyticsExportFormat, query?: AnalyticsRafflesQuery): Promise<Blob> =>
      client.getBlob(`${BASE_PATH}/raffles/export`, { query: { ...query, format } }),

    exportCollaborators: (
      format: AnalyticsExportFormat,
      query?: AnalyticsFiltersQuery,
    ): Promise<Blob> =>
      client.getBlob(`${BASE_PATH}/collaborators/export`, { query: { ...query, format } }),

    exportParticipants: (
      format: AnalyticsExportFormat,
      query?: AnalyticsFiltersQuery,
    ): Promise<Blob> =>
      client.getBlob(`${BASE_PATH}/participants/export`, { query: { ...query, format } }),
  };
}
