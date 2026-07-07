import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient } from '../client/fetcher';
import type { AuthUser, LoginRequest, RegisterRequest } from '../dto/auth';

const BASE_PATH = `${API_V1_PREFIX}/auth`;

/**
 * Cookie-based auth endpoints. The API sets/clears an httpOnly session cookie;
 * the client only ever sees the `AuthUser`. `skipAuth` is irrelevant now that
 * the session travels as a cookie, but register/login stay explicit as the
 * public (pre-session) surface.
 */
export function createAuthEndpoints(client: ApiClient) {
  return {
    register: (payload: RegisterRequest): Promise<AuthUser> =>
      client.post<AuthUser>(`${BASE_PATH}/register`, payload),

    login: (payload: LoginRequest): Promise<AuthUser> =>
      client.post<AuthUser>(`${BASE_PATH}/login`, payload),

    logout: (): Promise<void> => client.post<void>(`${BASE_PATH}/logout`),

    me: (): Promise<AuthUser> => client.get<AuthUser>(`${BASE_PATH}/me`),
  };
}
