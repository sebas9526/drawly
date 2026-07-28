/**
 * TanStack Query cache keys. Add one entry per resource as its endpoints
 * module is built — keeps cache keys stable and typo-proof across apps.
 *
 * Kept dependency-free (no import from @drawly/api-client, which already depends
 * on this package) — `status` is typed loosely as string on purpose.
 */
export const QUERY_KEYS = {
  health: ['health'] as const,
  authMe: ['auth', 'me'] as const,
  raffles: ['raffles'] as const,
  raffle: (id: string) => ['raffles', id] as const,
  /** Broad prefix for invalidating every tickets query at once (any raffle,
   * any status) — use instead of a raw `['tickets']` literal. */
  ticketsAll: ['tickets'] as const,
  tickets: (raffleId?: string, status?: string) =>
    ['tickets', { raffleId: raffleId ?? null, status: status ?? null }] as const,
  ticket: (id: string) => ['tickets', id] as const,
  availableTickets: (raffleId: string) => ['tickets', 'available', raffleId] as const,
  raffleTicketCounts: (raffleId: string) => ['tickets', 'counts', raffleId] as const,
  /** Broad prefix for invalidating every participants query at once. */
  participantsAll: ['participants'] as const,
  participants: (search?: string) => ['participants', { search: search ?? null }] as const,
  participant: (id: string) => ['participants', id] as const,
  participantTickets: (id: string) => ['participants', id, 'tickets'] as const,
  /** Broad prefix for invalidating every collaborators query at once. */
  collaboratorsAll: ['collaborators'] as const,
  collaborators: (raffleId?: string, search?: string) =>
    ['collaborators', { raffleId: raffleId ?? null, search: search ?? null }] as const,
  collaborator: (id: string) => ['collaborators', id] as const,
  raffleCollaborators: (raffleId: string) => ['collaborators', 'raffle', raffleId] as const,
  collaboratorStats: (raffleId: string) => ['collaborators', 'stats', raffleId] as const,
  /** Broad prefix for invalidating every public-portal query at once. */
  publicAll: ['public'] as const,
  publicCollaborators: (slug: string) => ['public', 'raffle', slug, 'collaborators'] as const,
  publicRaffle: (slug: string) => ['public', 'raffle', slug] as const,
  publicTickets: (slug: string) => ['public', 'raffle', slug, 'tickets'] as const,
  publicReferralRaffles: (collaboratorId: string) =>
    ['public', 'collaborator', collaboratorId, 'raffles'] as const,
  dashboardOverview: ['dashboard', 'overview'] as const,
  analyticsDashboard: (filters?: Record<string, unknown>) =>
    ['analytics', 'dashboard', filters ?? {}] as const,
  analyticsRaffles: (filters?: Record<string, unknown>, page?: number, pageSize?: number) =>
    ['analytics', 'raffles', filters ?? {}, page ?? 1, pageSize ?? 20] as const,
  analyticsRaffleDetail: (raffleId: string) => ['analytics', 'raffles', raffleId] as const,
  analyticsCollaborators: (filters?: Record<string, unknown>) =>
    ['analytics', 'collaborators', filters ?? {}] as const,
  analyticsParticipants: (filters?: Record<string, unknown>) =>
    ['analytics', 'participants', filters ?? {}] as const,
  analyticsSales: (filters?: Record<string, unknown>) =>
    ['analytics', 'sales', filters ?? {}] as const,
} as const;
