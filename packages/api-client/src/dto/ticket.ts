/**
 * Wire-format DTOs for the Tickets domain.
 * Field names are snake_case on purpose — they mirror the JSON the API sends
 * (apps/api tickets module + docs/04-api/API_SPECIFICATION.md), not internal TS
 * naming. Status values are lowercase to match the backend TicketStatus enum.
 */
export type TicketStatus = 'available' | 'reserved' | 'paid' | 'winner' | 'cancelled';

export interface TicketDto {
  id: string;
  raffle_id: string;
  participant_id: string | null;
  collaborator_id: string | null;
  number: number;
  status: TicketStatus;
  reserved_at: string | null;
  expires_at: string | null;
  sold_at: string | null;
  winner_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ListTicketsQuery {
  [key: string]: string | number | boolean | undefined | null;
  page?: number;
  page_size?: number;
  raffle_id?: string | undefined;
  status?: TicketStatus | undefined;
}

/** Admin single-ticket reservation body; both fields optional. */
export interface ReserveTicketRequest {
  participant_id?: string;
  collaborator_id?: string;
}
