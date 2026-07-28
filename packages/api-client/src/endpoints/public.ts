import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient, PaginatedResult } from '../client/fetcher';
import type {
  ListPublicTicketsQuery,
  PublicCollaboratorView,
  PublicRaffleView,
  PublicReferralRaffleView,
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

    /** Paginated (bounded per request even for a 100,000-ticket raffle);
     * see `fetchAllPages` for callers that still want the complete list. */
    listTickets: (
      slug: string,
      query?: ListPublicTicketsQuery,
    ): Promise<PaginatedResult<PublicTicketView>> =>
      client.getPaginated<PublicTicketView>(`${BASE_PATH}/raffles/${slug}/tickets`, {
        query,
        skipAuth: true,
      }),

    listCollaborators: (slug: string): Promise<PublicCollaboratorView[]> =>
      client.get<PublicCollaboratorView[]>(`${BASE_PATH}/raffles/${slug}/collaborators`, {
        skipAuth: true,
      }),

    /** A collaborator's currently-published raffles — resolves their
     * personal referral link (/ref/{collaboratorId}). */
    getReferralRaffles: (collaboratorId: string): Promise<PublicReferralRaffleView[]> =>
      client.get<PublicReferralRaffleView[]>(
        `${BASE_PATH}/collaborators/${collaboratorId}/raffles`,
        { skipAuth: true },
      ),

    reserveTicket: (slug: string, payload: PublicReserveRequest): Promise<PublicReserveResult> =>
      client.post<PublicReserveResult>(`${BASE_PATH}/raffles/${slug}/reserve`, payload, {
        skipAuth: true,
      }),
  };
}
