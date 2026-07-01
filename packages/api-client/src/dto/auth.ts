/**
 * PROVISIONAL — auth is explicitly out of MVP scope (docs/04-api/AUTHENTICATION.md
 * only describes the future flow: login -> access token -> refresh token ->
 * "Authorization: Bearer <token>"; no endpoint paths are documented yet).
 * These follow the same REST conventions as the rest of the API so the
 * client package has a stable shape to build against; adjust once the
 * backend auth module ships.
 */

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResult {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
}

export interface RefreshTokenRequest {
  refresh_token: string;
}
