import type { TicketStatus } from '@drawly/api-client';
import { useQuery } from '@tanstack/react-query';

import { QUERY_KEYS } from '@drawly/constants';

import { api } from '@/lib/api';

/** Tickets for a raffle, optionally filtered by status. */
export function useTickets(raffleId: string, status?: TicketStatus) {
  return useQuery({
    queryKey: QUERY_KEYS.tickets(raffleId, status),
    queryFn: () => api.tickets.list({ raffle_id: raffleId, status, page_size: 100 }),
    enabled: raffleId.length > 0,
  });
}

export interface RaffleTicketCounts {
  reserved: number;
  paid: number;
}

/** Reserved/paid ticket counts for a raffle, read from pagination totals
 * (page_size: 1) so raffle cards can show sales progress without fetching
 * every ticket row. */
export function useRaffleTicketCounts(raffleId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.raffleTicketCounts(raffleId),
    queryFn: async (): Promise<RaffleTicketCounts> => {
      const [reserved, paid] = await Promise.all([
        api.tickets.list({ raffle_id: raffleId, status: 'reserved', page_size: 1 }),
        api.tickets.list({ raffle_id: raffleId, status: 'paid', page_size: 1 }),
      ]);
      return { reserved: reserved.pagination.total, paid: paid.pagination.total };
    },
    enabled: raffleId.length > 0,
  });
}
