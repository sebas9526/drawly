/**
 * Wire-format DTOs for the Raffles domain.
 * Mirrors docs/04-api/API_SPECIFICATION.md and docs/02-architecture/DOMAIN_MODEL.md.
 * Field names are snake_case on purpose — they mirror the JSON the API sends,
 * not internal TS naming conventions.
 */
import type { ParticipantDto } from './participant';

export type RaffleStatus = 'draft' | 'published' | 'closed' | 'archived';

export interface RaffleDto {
  id: string;
  organization_id: string;
  title: string;
  description: string;
  prize: string;
  cover_image: string | null;
  ticket_price: number;
  total_tickets: number;
  /** First ticket number generated: 1 -> "1".."total", 0 -> "0"..(total-1).
   * Restricted to 0 or 1 by the API; fixed at creation and never editable
   * afterwards (absent from UpdateRaffleRequest). */
  starting_number: number;
  draw_date: string;
  status: RaffleStatus;
  public_slug: string;
  created_at: string;
  updated_at: string;
}

export interface CreateRaffleRequest {
  title: string;
  description: string;
  prize: string;
  ticket_price: number;
  total_tickets: number;
  starting_number?: number;
  draw_date: string;
}

export type UpdateRaffleRequest = Partial<Omit<CreateRaffleRequest, 'starting_number'>>;

export interface ListRafflesQuery {
  [key: string]: string | number | boolean | undefined | null;
  page?: number;
  page_size?: number;
  search?: string | undefined;
  status?: RaffleStatus | undefined;
  sort?: string | undefined;
}

export interface SelectWinnerResult {
  ticket: number;
  participant: ParticipantDto;
  winner_date: string;
}

/** Result of the explicit ticket-generation action (POST /raffles/{id}/tickets). */
export interface GenerateTicketsResult {
  raffle_id: string;
  generated: number;
}
