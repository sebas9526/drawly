import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient, PaginatedResult } from '../client/fetcher';
import type {
  ListParticipantsQuery,
  ParticipantDto,
  UpdateParticipantRequest,
} from '../dto/participant';

const BASE_PATH = `${API_V1_PREFIX}/participants`;

/** See docs/04-api/API_SPECIFICATION.md ("Participants"). */
export function createParticipantsEndpoints(client: ApiClient) {
  return {
    list: (query?: ListParticipantsQuery): Promise<PaginatedResult<ParticipantDto>> =>
      client.getPaginated<ParticipantDto>(BASE_PATH, { query }),

    get: (id: string): Promise<ParticipantDto> => client.get<ParticipantDto>(`${BASE_PATH}/${id}`),

    update: (id: string, payload: UpdateParticipantRequest): Promise<ParticipantDto> =>
      client.put<ParticipantDto>(`${BASE_PATH}/${id}`, payload),

    remove: (id: string): Promise<void> => client.delete<void>(`${BASE_PATH}/${id}`),
  };
}
