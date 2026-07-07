import type { AnalyticsFiltersQuery, AnalyticsRafflesQuery } from '@drawly/api-client';
import { useQuery } from '@tanstack/react-query';

import { QUERY_KEYS } from '@drawly/constants';

import { api } from '@/lib/api';

/** Every hook here is a plain read — the frontend never recomputes stats
 * itself, it only renders whatever the analytics endpoints already computed. */
export function useAnalyticsDashboard(filters: AnalyticsFiltersQuery) {
  return useQuery({
    queryKey: QUERY_KEYS.analyticsDashboard(filters),
    queryFn: () => api.analytics.getDashboard(filters),
  });
}

export function useAnalyticsSales(filters: AnalyticsFiltersQuery) {
  return useQuery({
    queryKey: QUERY_KEYS.analyticsSales(filters),
    queryFn: () => api.analytics.getSales(filters),
  });
}

export function useAnalyticsRaffles(
  filters: AnalyticsRafflesQuery,
  page: number,
  pageSize: number,
) {
  return useQuery({
    queryKey: QUERY_KEYS.analyticsRaffles(filters, page, pageSize),
    queryFn: () => api.analytics.getRaffles({ ...filters, page, page_size: pageSize }),
  });
}

export function useAnalyticsRaffleDetail(raffleId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.analyticsRaffleDetail(raffleId),
    queryFn: () => api.analytics.getRaffleDetail(raffleId),
    enabled: raffleId.length > 0,
  });
}

export function useAnalyticsCollaborators(filters: AnalyticsFiltersQuery) {
  return useQuery({
    queryKey: QUERY_KEYS.analyticsCollaborators(filters),
    queryFn: () => api.analytics.getCollaborators(filters),
  });
}

export function useAnalyticsParticipants(filters: AnalyticsFiltersQuery) {
  return useQuery({
    queryKey: QUERY_KEYS.analyticsParticipants(filters),
    queryFn: () => api.analytics.getParticipants(filters),
  });
}
