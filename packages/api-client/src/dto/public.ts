/**
 * Wire-format DTOs for the public reservation portal. These are deliberately
 * minimal projections — no internal ids, no participant data, no admin fields.
 */
import type { TicketStatus } from './ticket';

export interface PublicRaffleView {
  public_slug: string;
  title: string;
  description: string;
  prize: string;
  cover_image: string | null;
  ticket_price: number;
  draw_date: string;
  total_tickets: number;
  starting_number: number;
  available_count: number;
  reserved_count: number;
  paid_count: number;
}

export interface PublicTicketView {
  number: number;
  status: TicketStatus;
}

export interface ListPublicTicketsQuery {
  [key: string]: string | number | boolean | undefined | null;
  page?: number;
  page_size?: number;
}

export interface PublicCollaboratorView {
  id: string;
  name: string;
  color: string;
}

export interface PublicReserveRequest {
  ticket_number: number;
  participant: {
    full_name: string;
    phone: string;
    email?: string | undefined;
    document?: string | undefined;
  };
  /** Optional seller credited with the reservation. */
  collaborator_id?: string | null | undefined;
}

export interface PublicReserveResult {
  ticket_number: number;
  raffle_title: string;
  status: TicketStatus;
}
