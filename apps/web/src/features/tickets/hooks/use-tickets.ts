import type { TicketStatus } from '@drawly/api-client';
import { fetchAllPages } from '@drawly/api-client';
import { useQuery } from '@tanstack/react-query';

import { QUERY_KEYS } from '@drawly/constants';

import { api } from '@/lib/api';

/** Tickets for a raffle, optionally filtered by status. A raffle can have up
 * to 100,000 tickets, and the admin table still expects the complete set
 * client-side (search/filter/bulk-select), so every page is fetched — but
 * each request stays bounded instead of the previous single unbounded fetch. */
export function useTickets(raffleId: string, status?: TicketStatus) {
  return useQuery({
    queryKey: QUERY_KEYS.tickets(raffleId, status),
    queryFn: () =>
      fetchAllPages((page, pageSize) =>
        api.tickets.list({ raffle_id: raffleId, status, page, page_size: pageSize }),
      ),
    enabled: raffleId.length > 0,
  });
}

export interface RaffleTicketCounts {
  reserved: number;
  paid: number;
  /** Tickets actually generated in the DB so far — distinct from the
   * raffle's configured `total_tickets`, which stays the same whether or
   * not "Generar boletas" has been run yet. */
  generated: number;
}

/** Reserved/paid/generated ticket counts for a raffle, read from pagination
 * totals (page_size: 1) so raffle cards can show sales progress (and whether
 * tickets exist at all) without fetching every ticket row. */
export function useRaffleTicketCounts(raffleId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.raffleTicketCounts(raffleId),
    queryFn: async (): Promise<RaffleTicketCounts> => {
      const [reserved, paid, generated] = await Promise.all([
        api.tickets.list({ raffle_id: raffleId, status: 'reserved', page_size: 1 }),
        api.tickets.list({ raffle_id: raffleId, status: 'paid', page_size: 1 }),
        api.tickets.list({ raffle_id: raffleId, page_size: 1 }),
      ]);
      return {
        reserved: reserved.pagination.total,
        paid: paid.pagination.total,
        generated: generated.pagination.total,
      };
    },
    enabled: raffleId.length > 0,
  });
}
