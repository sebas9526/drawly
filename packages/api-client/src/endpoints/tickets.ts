import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient, PaginatedResult } from '../client/fetcher';
import type { ListTicketsQuery, TicketDto, UpdateTicketRequest } from '../dto/ticket';

const BASE_PATH = `${API_V1_PREFIX}/tickets`;

/** See docs/04-api/API_SPECIFICATION.md ("Tickets"). */
export function createTicketsEndpoints(client: ApiClient) {
  return {
    list: (query?: ListTicketsQuery): Promise<PaginatedResult<TicketDto>> =>
      client.getPaginated<TicketDto>(BASE_PATH, { query }),

    get: (id: string): Promise<TicketDto> => client.get<TicketDto>(`${BASE_PATH}/${id}`),

    update: (id: string, payload: UpdateTicketRequest): Promise<TicketDto> =>
      client.patch<TicketDto>(`${BASE_PATH}/${id}`, payload),

    cancelReservation: (id: string): Promise<TicketDto> =>
      client.patch<TicketDto>(`${BASE_PATH}/${id}/cancel`),
  };
}
