/**
 * TanStack Query cache keys. Add one entry per resource as its endpoints
 * module is built — keeps cache keys stable and typo-proof across apps.
 */
export const QUERY_KEYS = {
  health: ['health'] as const,
} as const;
