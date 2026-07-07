import type { TicketStatus } from '@drawly/api-client';
import type { Tone } from '@drawly/ui/tones';

/** Presentation of each ticket status: label (Spanish) + UI tone. */
export const TICKET_STATUS_PRESENTATION: Record<TicketStatus, { label: string; tone: Tone }> = {
  available: { label: 'Disponible', tone: 'success' },
  reserved: { label: 'Reservada', tone: 'warning' },
  paid: { label: 'Pagada', tone: 'info' },
  winner: { label: 'Ganadora', tone: 'primary' },
  cancelled: { label: 'Cancelada', tone: 'neutral' },
};

export const TICKET_STATUS_LABELS: Record<TicketStatus, string> = {
  available: TICKET_STATUS_PRESENTATION.available.label,
  reserved: TICKET_STATUS_PRESENTATION.reserved.label,
  paid: TICKET_STATUS_PRESENTATION.paid.label,
  winner: TICKET_STATUS_PRESENTATION.winner.label,
  cancelled: TICKET_STATUS_PRESENTATION.cancelled.label,
};

export const TICKET_STATUS_OPTIONS: readonly TicketStatus[] = [
  'available',
  'reserved',
  'paid',
  'winner',
  'cancelled',
] as const;
