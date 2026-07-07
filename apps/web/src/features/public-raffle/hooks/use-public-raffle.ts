import type { PublicReserveRequest } from '@drawly/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { QUERY_KEYS } from '@drawly/constants';

import { api } from '@/lib/api';

/** Availability refresh interval (polling). Swappable for SSE/WebSockets later
 * without touching the domain. */
const POLL_INTERVAL_MS = 12_000;

export function usePublicRaffle(slug: string) {
  return useQuery({
    queryKey: QUERY_KEYS.publicRaffle(slug),
    queryFn: () => api.public.getRaffle(slug),
    enabled: slug.length > 0,
  });
}

export function usePublicCollaborators(slug: string) {
  return useQuery({
    queryKey: QUERY_KEYS.publicCollaborators(slug),
    queryFn: () => api.public.listCollaborators(slug),
    enabled: slug.length > 0,
  });
}

export function usePublicTickets(slug: string) {
  return useQuery({
    queryKey: QUERY_KEYS.publicTickets(slug),
    queryFn: () => api.public.listTickets(slug),
    enabled: slug.length > 0,
    refetchInterval: POLL_INTERVAL_MS,
    refetchIntervalInBackground: false,
  });
}

export function usePublicReserve(slug: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: PublicReserveRequest) => api.public.reserveTicket(slug, payload),
    // Refresh availability + stats after any attempt (success or "taken").
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ['public'] });
    },
  });
}
