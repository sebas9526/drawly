/**
 * Wire-format DTOs for the Raffles domain.
 * Mirrors docs/04-api/API_SPECIFICATION.md and docs/02-architecture/DOMAIN_MODEL.md.
 * Field names are snake_case on purpose — they mirror the JSON the API sends,
 * not internal TS naming conventions.
 */

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
  /** Optional scheduled activation: when set, the raffle publishes itself
   * automatically once this moment passes (still requires tickets to
   * already be generated). null means "no schedule" — publish manually. */
  publish_at: string | null;
  status: RaffleStatus;
  public_slug: string;
  /** Set only once a *valid* (paid) winner closes the raffle — drives the
   * cleanup sweep that removes a concluded raffle after a grace period. */
  closed_at: string | null;
  /** Reflects the last winner-registration attempt, valid or not. If
   * `status` is 'closed', this ticket is the confirmed winner. If `status`
   * is still 'published' and this is set, the last entered number wasn't
   * paid — an unresolved attempt, not a hard block. */
  winner_ticket_id: string | null;
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
  publish_at?: string | undefined;
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

export interface RegisterWinnerRequest {
  ticket_number: number;
}

/** Response for PATCH /raffles/{id}/winner. `valid: false` means the entered
 * number wasn't paid — nothing closed, no winner confirmed, and the caller
 * can just retry with another number. */
export interface RegisterWinnerResult {
  valid: boolean;
  ticket_number: number;
  participant_id: string | null;
  winner_at: string | null;
}

/** Result of the explicit ticket-generation action (POST /raffles/{id}/tickets). */
export interface GenerateTicketsResult {
  raffle_id: string;
  generated: number;
}
