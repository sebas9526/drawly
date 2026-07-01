import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient } from '../client/fetcher';
import type { LoginRequest, LoginResult, RefreshTokenRequest } from '../dto/auth';

const BASE_PATH = `${API_V1_PREFIX}/auth`;

/** PROVISIONAL — see the note in ../dto/auth.ts. */
export function createAuthEndpoints(client: ApiClient) {
  return {
    login: (payload: LoginRequest): Promise<LoginResult> =>
      client.post<LoginResult>(`${BASE_PATH}/login`, payload, { skipAuth: true }),

    refresh: (payload: RefreshTokenRequest): Promise<LoginResult> =>
      client.post<LoginResult>(`${BASE_PATH}/refresh`, payload, { skipAuth: true }),

    logout: (): Promise<void> => client.post<void>(`${BASE_PATH}/logout`),
  };
}
