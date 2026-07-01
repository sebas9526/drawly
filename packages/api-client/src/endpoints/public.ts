import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient } from '../client/fetcher';
import type { RaffleDto } from '../dto/raffle';
import type { ReserveTicketsRequest, TicketDto } from '../dto/ticket';

const BASE_PATH = `${API_V1_PREFIX}/public`;

/**
 * Unauthenticated endpoints used by the public raffle page.
 * See docs/04-api/API_SPECIFICATION.md ("Public Raffles").
 */
export function createPublicEndpoints(client: ApiClient) {
  return {
    getRaffle: (slug: string): Promise<RaffleDto> =>
      client.get<RaffleDto>(`${BASE_PATH}/${slug}`, { skipAuth: true }),

    getAvailableTickets: (slug: string): Promise<TicketDto[]> =>
      client.get<TicketDto[]>(`${BASE_PATH}/${slug}/tickets`, { skipAuth: true }),

    reserveTickets: (slug: string, payload: ReserveTicketsRequest): Promise<TicketDto[]> =>
      client.post<TicketDto[]>(`${BASE_PATH}/${slug}/reserve`, payload, { skipAuth: true }),
  };
}
