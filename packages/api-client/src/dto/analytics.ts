/**
 * Wire-format DTOs for the Analytics & Reports module (Sprint 9).
 * Field names are snake_case on purpose — they mirror the JSON the API sends
 * (apps/api `modules/analytics`), not internal TS naming conventions.
 */
import type { RaffleStatus } from './raffle';
import type { TicketStatus } from './ticket';

export interface ExecutiveDashboard {
  raffles_total: number;
  raffles_published: number;
  raffles_closed: number;
  tickets_available: number;
  tickets_reserved: number;
  tickets_paid: number;
  participants_total: number;
  collaborators_total: number;
  /** "Ingresos esperados": total_tickets * ticket_price across matched raffles. */
  expected_revenue: number;
  /** "Ingresos recibidos": sum of ticket_price for PAID tickets — a seat for
   * the future Payments module, not a real transaction yet. */
  received_revenue: number;
  percent_sold: number;
  percent_reserved: number;
}

export interface RankingEntry {
  id: string;
  name: string;
  count: number;
  value: number;
  rank: number;
}

export interface RaffleReportRow {
  id: string;
  title: string;
  status: RaffleStatus;
  created_at: string;
  draw_date: string;
  total_tickets: number;
  available: number;
  reserved: number;
  paid: number;
  percent_sold: number;
  expected_revenue: number;
}

export interface RaffleReportDetail extends RaffleReportRow {
  top_collaborators: RankingEntry[];
  top_participants: RankingEntry[];
}

export interface CollaboratorReportRow {
  id: string;
  name: string;
  raffle_id: string;
  raffle_title: string;
  total_sales: number;
  total_reservations: number;
  participants_served: number;
  expected_amount: number;
  participation_percent: number;
  rank: number;
}

export interface ParticipantReportRow {
  id: string;
  full_name: string;
  purchases_count: number;
  tickets_count: number;
  amount_invested: number;
  last_purchase_at: string | null;
  raffles_count: number;
}

export interface TimeSeriesPoint {
  day: string;
  count: number;
  value: number;
}

export interface TicketStatusDistribution {
  available: number;
  reserved: number;
  paid: number;
  cancelled: number;
  winner: number;
}

export interface GlobalReports {
  top_collaborators: RankingEntry[];
  top_raffles: RankingEntry[];
  top_participants: RankingEntry[];
  sales_by_day: TimeSeriesPoint[];
  reservations_by_day: TimeSeriesPoint[];
  status_distribution: TicketStatusDistribution;
}

/** Shared filters accepted by every analytics endpoint (see
 * docs/04-api/API_SPECIFICATION.md, "Analytics"). `status` is a ticket status;
 * it does not apply to the raffles report (see `raffle_status` below). */
export interface AnalyticsFiltersQuery {
  [key: string]: string | number | boolean | undefined | null;
  start_date?: string | undefined;
  end_date?: string | undefined;
  raffle_id?: string | undefined;
  status?: TicketStatus | undefined;
  collaborator_id?: string | undefined;
}

export interface AnalyticsRafflesQuery extends AnalyticsFiltersQuery {
  raffle_status?: RaffleStatus | undefined;
  page?: number;
  page_size?: number;
}

export interface AnalyticsCollaboratorsQuery extends AnalyticsFiltersQuery {
  page?: number;
  page_size?: number;
}

export interface AnalyticsParticipantsQuery extends AnalyticsFiltersQuery {
  page?: number;
  page_size?: number;
}

export type AnalyticsExportFormat = 'excel' | 'pdf';
