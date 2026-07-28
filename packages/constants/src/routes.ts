/**
 * Frontend app routes. Feature modules add their own entries here as they're
 * built instead of hardcoding paths inline.
 */
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  RAFFLES: '/raffles',
  RAFFLE_TICKETS: (raffleId: string) => `/raffles/${raffleId}/tickets`,
  PARTICIPANTS: '/participants',
  PARTICIPANT_DETAIL: (participantId: string) => `/participants/${participantId}`,
  COLLABORATORS: '/collaborators',
  REPORTS: '/reports',
  REPORTS_RAFFLES: '/reports/raffles',
  REPORTS_COLLABORATORS: '/reports/collaborators',
  REPORTS_PARTICIPANTS: '/reports/participants',
  PUBLIC_RAFFLE: (slug: string) => `/r/${slug}`,
  REFERRAL: (collaboratorId: string) => `/ref/${collaboratorId}`,
} as const;
