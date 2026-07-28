import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient, PaginatedResult } from '../client/fetcher';
import type {
  CreateRaffleRequest,
  GenerateTicketsResult,
  ListRafflesQuery,
  RaffleDto,
  RegisterWinnerRequest,
  RegisterWinnerResult,
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

    /** Explicit ticket generation for a raffle (Sprint 3). Generates the
     * raffle's configured `total_tickets`; fails if already generated. */
    generateTickets: (id: string): Promise<GenerateTicketsResult> =>
      client.post<GenerateTicketsResult>(`${BASE_PATH}/${id}/tickets`),

    publish: (id: string): Promise<RaffleDto> =>
      client.patch<RaffleDto>(`${BASE_PATH}/${id}/publish`),

    close: (id: string): Promise<RaffleDto> => client.patch<RaffleDto>(`${BASE_PATH}/${id}/close`),

    /** Manual winner entry: looks up the ticket by number, confirms it as
     * winner and closes the raffle if it's paid, or just records the
     * attempt (raffle stays open) if it isn't yet. */
    registerWinner: (id: string, payload: RegisterWinnerRequest): Promise<RegisterWinnerResult> =>
      client.patch<RegisterWinnerResult>(`${BASE_PATH}/${id}/winner`, payload),
  };
}
