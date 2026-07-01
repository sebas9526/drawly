/**
 * localStorage/secure-storage keys shared across clients.
 * Mirrors the future JWT flow described in docs/04-api/AUTHENTICATION.md.
 */
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'drawly.access_token',
  REFRESH_TOKEN: 'drawly.refresh_token',
} as const;
