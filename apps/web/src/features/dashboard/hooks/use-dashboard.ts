import { useQuery } from '@tanstack/react-query';

import { QUERY_KEYS } from '@drawly/constants';

import { api } from '@/lib/api';

/** Auto-refresh interval for the dashboard (polling). Swappable for SSE later. */
const REFRESH_INTERVAL_MS = 30_000;

export function useDashboardOverview() {
  return useQuery({
    queryKey: QUERY_KEYS.dashboardOverview,
    queryFn: () => api.dashboard.getOverview(),
    refetchInterval: REFRESH_INTERVAL_MS,
    refetchIntervalInBackground: false,
  });
}
