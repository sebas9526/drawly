import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient } from '../client/fetcher';
import type { DashboardStatsDto } from '../dto/dashboard';

/** See docs/04-api/API_SPECIFICATION.md ("Dashboard"). */
export function createDashboardEndpoints(client: ApiClient) {
  return {
    getStats: (): Promise<DashboardStatsDto> =>
      client.get<DashboardStatsDto>(`${API_V1_PREFIX}/dashboard`),
  };
}
