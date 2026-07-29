import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient, PaginatedResult } from '../client/fetcher';
import type {
  CollaboratorDto,
  CollaboratorStatsDto,
  CreateCollaboratorRequest,
  ListCollaboratorsQuery,
  SetRaffleCollaboratorsRequest,
  UpdateCollaboratorRequest,
} from '../dto/collaborator';

const BASE_PATH = `${API_V1_PREFIX}/collaborators`;

/**
 * Strongly-typed collaborator admin endpoints, mirroring the collaborators
 * module routes in apps/api. Every method returns already-unwrapped data.
 * See docs/04-api/API_SPECIFICATION.md ("Collaborators").
 */
export function createCollaboratorsEndpoints(client: ApiClient) {
  return {
    getAll: (query?: ListCollaboratorsQuery): Promise<PaginatedResult<CollaboratorDto>> =>
      client.getPaginated<CollaboratorDto>(BASE_PATH, { query }),

    getById: (id: string): Promise<CollaboratorDto> =>
      client.get<CollaboratorDto>(`${BASE_PATH}/${id}`),

    getByRaffle: (raffleId: string, activeOnly = false): Promise<CollaboratorDto[]> =>
      client.get<CollaboratorDto[]>(`${BASE_PATH}/raffle/${raffleId}`, {
        query: { active_only: activeOnly },
      }),

    statsByRaffle: (raffleId: string): Promise<CollaboratorStatsDto[]> =>
      client.get<CollaboratorStatsDto[]>(`${BASE_PATH}/raffle/${raffleId}/stats`),

    setForRaffle: (
      raffleId: string,
      payload: SetRaffleCollaboratorsRequest,
    ): Promise<CollaboratorDto[]> =>
      client.put<CollaboratorDto[]>(`${BASE_PATH}/raffle/${raffleId}`, payload),

    create: (payload: CreateCollaboratorRequest): Promise<CollaboratorDto> =>
      client.post<CollaboratorDto>(BASE_PATH, payload),

    update: (id: string, payload: UpdateCollaboratorRequest): Promise<CollaboratorDto> =>
      client.put<CollaboratorDto>(`${BASE_PATH}/${id}`, payload),

    activate: (id: string): Promise<CollaboratorDto> =>
      client.patch<CollaboratorDto>(`${BASE_PATH}/${id}/activate`),

    deactivate: (id: string): Promise<CollaboratorDto> =>
      client.patch<CollaboratorDto>(`${BASE_PATH}/${id}/deactivate`),

    delete: (id: string): Promise<void> => client.delete<void>(`${BASE_PATH}/${id}`),
  };
}
