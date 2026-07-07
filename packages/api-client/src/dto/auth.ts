/**
 * Auth DTOs mirroring the backend Users module (docs/04-api/AUTHENTICATION.md).
 * The session is carried in an httpOnly cookie set by the API, so no token is
 * ever handled in JS. `me` returns the authenticated user; login/register set
 * the cookie as a side effect.
 */

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthUser {
  id: string;
  full_name: string;
  email: string;
  avatar_url: string | null;
  email_verified_at: string | null;
  created_at: string;
}
