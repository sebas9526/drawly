import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient, PaginatedResult } from '../client/fetcher';
import type { ListTicketsQuery, ReserveTicketRequest, TicketDto } from '../dto/ticket';

const BASE_PATH = `${API_V1_PREFIX}/tickets`;

/**
 * Strongly-typed ticket admin endpoints, mirroring the tickets module routes in
 * apps/api. Every method returns already-unwrapped data (ApiClient parses the
 * response envelope). See docs/04-api/API_SPECIFICATION.md ("Tickets").
 */
export function createTicketsEndpoints(client: ApiClient) {
  return {
    /** Paginated tickets, filterable by raffle and status. */
    list: (query?: ListTicketsQuery): Promise<PaginatedResult<TicketDto>> =>
      client.getPaginated<TicketDto>(BASE_PATH, { query }),

    /** Only AVAILABLE tickets for a raffle (non-paginated). */
    listAvailable: (raffleId: string): Promise<TicketDto[]> =>
      client.get<TicketDto[]>(`${BASE_PATH}/available`, { query: { raffle_id: raffleId } }),

    getById: (id: string): Promise<TicketDto> => client.get<TicketDto>(`${BASE_PATH}/${id}`),

    reserve: (id: string, payload: ReserveTicketRequest = {}): Promise<TicketDto> =>
      client.patch<TicketDto>(`${BASE_PATH}/${id}/reserve`, payload),

    cancelReservation: (id: string): Promise<TicketDto> =>
      client.patch<TicketDto>(`${BASE_PATH}/${id}/cancel`),

    markAsPaid: (id: string): Promise<TicketDto> =>
      client.patch<TicketDto>(`${BASE_PATH}/${id}/pay`),

    /** Assign or change the participant on a ticket (reserves it if available). */
    assignParticipant: (id: string, participantId: string): Promise<TicketDto> =>
      client.patch<TicketDto>(`${BASE_PATH}/${id}/participant`, { participant_id: participantId }),

    /** Remove the participant, releasing the reserved ticket back to available. */
    unassignParticipant: (id: string): Promise<TicketDto> =>
      client.delete<TicketDto>(`${BASE_PATH}/${id}/participant`),

    /** Credit or clear the collaborator (seller) on a reserved ticket. */
    setCollaborator: (id: string, collaboratorId: string | null): Promise<TicketDto> =>
      client.patch<TicketDto>(`${BASE_PATH}/${id}/collaborator`, {
        collaborator_id: collaboratorId,
      }),
  };
}
