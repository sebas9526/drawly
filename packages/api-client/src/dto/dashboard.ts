/**
 * Wire-format DTOs for the admin dashboard. The overview is a single aggregated
 * payload (one request) — see docs/04-api/API_SPECIFICATION.md ("Dashboard").
 */
import type { RaffleStatus } from './raffle';

export interface DashboardRaffleCounts {
  total: number;
  active: number;
  draft: number;
  published: number;
  closed: number;
  archived: number;
}

export interface DashboardTicketCounts {
  total: number;
  available: number;
  reserved: number;
  paid: number;
}

export interface DashboardSalesSummary {
  potential_value: number;
  reserved_value: number;
  paid_value: number;
}

export interface DashboardRecentReservation {
  number: number;
  raffle_title: string;
  participant_name: string | null;
  reserved_at: string;
}

export interface DashboardRecentRaffle {
  title: string;
  status: RaffleStatus;
  total_tickets: number;
  available_count: number;
}

export interface DashboardOverview {
  raffles: DashboardRaffleCounts;
  tickets: DashboardTicketCounts;
  participants: number;
  collaborators: number;
  sales: DashboardSalesSummary;
  recent_reservations: DashboardRecentReservation[];
  recent_raffles: DashboardRecentRaffle[];
}
