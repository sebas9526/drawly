import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient } from '../client/fetcher';
import type {
  PublicCollaboratorView,
  PublicRaffleView,
  PublicReserveRequest,
  PublicReserveResult,
  PublicTicketView,
} from '../dto/public';

const BASE_PATH = `${API_V1_PREFIX}/public`;

/**
 * Unauthenticated endpoints for the public reservation portal. Separate surface
 * from the admin endpoints; never exposes internal ids or participant data.
 * See docs/04-api/API_SPECIFICATION.md ("Public Portal").
 */
export function createPublicEndpoints(client: ApiClient) {
  return {
    getRaffle: (slug: string): Promise<PublicRaffleView> =>
      client.get<PublicRaffleView>(`${BASE_PATH}/raffles/${slug}`, { skipAuth: true }),

    listTickets: (slug: string): Promise<PublicTicketView[]> =>
      client.get<PublicTicketView[]>(`${BASE_PATH}/raffles/${slug}/tickets`, { skipAuth: true }),

    listCollaborators: (slug: string): Promise<PublicCollaboratorView[]> =>
      client.get<PublicCollaboratorView[]>(`${BASE_PATH}/raffles/${slug}/collaborators`, {
        skipAuth: true,
      }),

    reserveTicket: (slug: string, payload: PublicReserveRequest): Promise<PublicReserveResult> =>
      client.post<PublicReserveResult>(`${BASE_PATH}/raffles/${slug}/reserve`, payload, {
        skipAuth: true,
      }),
  };
}
