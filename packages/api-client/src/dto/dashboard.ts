/** GET /dashboard — see docs/04-api/API_SPECIFICATION.md. */
export interface DashboardStatsDto {
  active_raffles: number;
  revenue: number;
  participants: number;
  reserved_tickets: number;
  available_tickets: number;
  closed_raffles: number;
}
