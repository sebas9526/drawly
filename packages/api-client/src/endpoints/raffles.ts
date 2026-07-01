import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient, PaginatedResult } from '../client/fetcher';
import type {
  CreateRaffleRequest,
  ListRafflesQuery,
  RaffleDto,
  SelectWinnerResult,
  UpdateRaffleRequest,
} from '../dto/raffle';

const BASE_PATH = `${API_V1_PREFIX}/raffles`;

/** See docs/04-api/API_SPECIFICATION.md ("Raffles"). */
export function createRafflesEndpoints(client: ApiClient) {
  return {
    list: (query?: ListRafflesQuery): Promise<PaginatedResult<RaffleDto>> =>
      client.getPaginated<RaffleDto>(BASE_PATH, { query }),

    get: (id: string): Promise<RaffleDto> => client.get<RaffleDto>(`${BASE_PATH}/${id}`),

    create: (payload: CreateRaffleRequest): Promise<RaffleDto> =>
      client.post<RaffleDto>(BASE_PATH, payload),

    update: (id: string, payload: UpdateRaffleRequest): Promise<RaffleDto> =>
      client.put<RaffleDto>(`${BASE_PATH}/${id}`, payload),

    remove: (id: string): Promise<void> => client.delete<void>(`${BASE_PATH}/${id}`),

    publish: (id: string): Promise<RaffleDto> =>
      client.patch<RaffleDto>(`${BASE_PATH}/${id}/publish`),

    close: (id: string): Promise<RaffleDto> => client.patch<RaffleDto>(`${BASE_PATH}/${id}/close`),

    selectWinner: (id: string): Promise<SelectWinnerResult> =>
      client.post<SelectWinnerResult>(`${BASE_PATH}/${id}/winner`),
  };
}
