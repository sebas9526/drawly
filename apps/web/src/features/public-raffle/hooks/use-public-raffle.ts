import type { PublicReserveRequest } from '@drawly/api-client';
import { fetchAllPages } from '@drawly/api-client';
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

/** A collaborator's personal referral link (/ref/{id}) resolves to this —
 * their currently-published raffles. */
export function usePublicReferralRaffles(collaboratorId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.publicReferralRaffles(collaboratorId),
    queryFn: () => api.public.getReferralRaffles(collaboratorId),
    enabled: collaboratorId.length > 0,
    retry: false,
  });
}

export function usePublicTickets(slug: string) {
  return useQuery({
    queryKey: QUERY_KEYS.publicTickets(slug),
    queryFn: () =>
      fetchAllPages((page, pageSize) =>
        api.public.listTickets(slug, { page, page_size: pageSize }),
      ),
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
      void queryClient.invalidateQueries({ queryKey: QUERY_KEYS.publicAll });
    },
  });
}
