import type { AuthTokenProvider } from '../types/config';

/**
 * Centralized authentication: every request routes through here so there is
 * exactly one place that knows how to attach a bearer token.
 * See docs/04-api/AUTHENTICATION.md ("Authorization: Bearer <token>").
 */
export async function withAuthHeader(
  headers: Record<string, string>,
  getToken?: AuthTokenProvider,
): Promise<Record<string, string>> {
  if (!getToken) return headers;

  const token = await getToken();
  if (!token) return headers;

  return { ...headers, Authorization: `Bearer ${token}` };
}
