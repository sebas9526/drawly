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
  /** Set only once the raffle is closed with a confirmed (paid) winner —
   * never for an unresolved attempt. No phone/document, just enough for a
   * public announcement. */
  winner_ticket_number: number | null;
  winner_participant_name: string | null;
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

/** One of a collaborator's published raffles, shown on their personal
 * referral link (/ref/{collaboratorId}) when they sell for more than one. */
export interface PublicReferralRaffleView {
  public_slug: string;
  title: string;
  prize: string;
  cover_image: string | null;
}

export interface PublicReserveRequest {
  ticket_number: number;
  participant: {
    full_name: string;
    phone: string;
    email?: string | undefined;
    document?: string | undefined;
  };
  /** Seller credited with the reservation — required (public flow only). */
  collaborator_id: string;
}

export interface PublicReserveResult {
  ticket_number: number;
  raffle_title: string;
  status: TicketStatus;
}
