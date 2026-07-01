import type { QueryParams } from '../types/config';

/** Builds a "?a=1&b=2" query string, dropping null/undefined values. Empty when there's nothing to add. */
export function buildQueryString(params?: QueryParams): string {
  if (!params) return '';

  const search = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null) continue;
    search.set(key, String(value));
  }

  const serialized = search.toString();
  return serialized ? `?${serialized}` : '';
}
