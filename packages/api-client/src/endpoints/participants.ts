import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient, PaginatedResult } from '../client/fetcher';
import type {
  CreateParticipantRequest,
  ListParticipantsQuery,
  ParticipantDto,
  UpdateParticipantRequest,
} from '../dto/participant';
import type { TicketDto } from '../dto/ticket';

const BASE_PATH = `${API_V1_PREFIX}/participants`;

/**
 * Strongly-typed participant admin endpoints, mirroring the participants module
 * routes in apps/api. See docs/04-api/API_SPECIFICATION.md ("Participants").
 */
export function createParticipantsEndpoints(client: ApiClient) {
  return {
    list: (query?: ListParticipantsQuery): Promise<PaginatedResult<ParticipantDto>> =>
      client.getPaginated<ParticipantDto>(BASE_PATH, { query }),

    getById: (id: string): Promise<ParticipantDto> =>
      client.get<ParticipantDto>(`${BASE_PATH}/${id}`),

    create: (payload: CreateParticipantRequest): Promise<ParticipantDto> =>
      client.post<ParticipantDto>(BASE_PATH, payload),

    update: (id: string, payload: UpdateParticipantRequest): Promise<ParticipantDto> =>
      client.patch<ParticipantDto>(`${BASE_PATH}/${id}`, payload),

    remove: (id: string): Promise<void> => client.delete<void>(`${BASE_PATH}/${id}`),

    /** All tickets currently assigned to the participant (their history). */
    getTickets: (id: string): Promise<TicketDto[]> =>
      client.get<TicketDto[]>(`${BASE_PATH}/${id}/tickets`),
  };
}
