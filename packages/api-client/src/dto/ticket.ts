export type TicketStatus = 'available' | 'reserved' | 'paid' | 'winner' | 'cancelled';

export interface TicketDto {
  id: string;
  raffle_id: string;
  participant_id: string | null;
  number: number;
  status: TicketStatus;
  reserved_at: string | null;
  sold_at: string | null;
  winner_at: string | null;
  created_at: string;
  updated_at: string;
}

export type UpdateTicketRequest = Partial<Pick<TicketDto, 'status'>>;

export interface ListTicketsQuery {
  [key: string]: string | number | boolean | undefined | null;
  page?: number;
  page_size?: number;
  raffle_id?: string;
  status?: TicketStatus;
}

export interface ReserveTicketsRequest {
  participant: {
    full_name: string;
    phone: string;
    email?: string;
    address?: string;
    city?: string;
  };
  tickets: number[];
}
