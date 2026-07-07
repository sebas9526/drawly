import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient } from '../client/fetcher';
import type {
  DashboardOverview,
  DashboardRecentRaffle,
  DashboardRecentReservation,
} from '../dto/dashboard';

const BASE_PATH = `${API_V1_PREFIX}/dashboard`;

/**
 * Admin dashboard endpoints. Prefer `getOverview` — it returns everything in a
 * single aggregated request. See docs/04-api/API_SPECIFICATION.md ("Dashboard").
 */
export function createDashboardEndpoints(client: ApiClient) {
  return {
    getOverview: (): Promise<DashboardOverview> =>
      client.get<DashboardOverview>(`${BASE_PATH}/overview`),

    getRecentReservations: (): Promise<DashboardRecentReservation[]> =>
      client.get<DashboardRecentReservation[]>(`${BASE_PATH}/reservations`),

    getRecentRaffles: (): Promise<DashboardRecentRaffle[]> =>
      client.get<DashboardRecentRaffle[]>(`${BASE_PATH}/raffles`),
  };
}
