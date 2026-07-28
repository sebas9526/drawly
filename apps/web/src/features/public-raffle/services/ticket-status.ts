import type { TicketStatus } from '@drawly/api-client';

/** Public presentation of ticket status: label + dot color (token-based, so it
 * adapts to light/dark) + selectability. No participant/admin data is shown. */
export interface TicketStatusStyle {
  label: string;
  dotClass: string;
  cellClass: string;
  selectable: boolean;
}

export const PUBLIC_TICKET_STATUS: Record<TicketStatus, TicketStatusStyle> = {
  available: {
    label: 'Disponible',
    dotClass: 'bg-success',
    cellClass: 'border-border hover:border-primary hover:bg-primary/5 cursor-pointer',
    selectable: true,
  },
  reserved: {
    label: 'Reservada',
    dotClass: 'bg-warning',
    cellClass: 'border-border/60 bg-warning/5 cursor-not-allowed',
    selectable: false,
  },
  paid: {
    label: 'Pagada',
    dotClass: 'bg-info',
    cellClass: 'border-border/60 bg-info/5 cursor-not-allowed',
    selectable: false,
  },
  winner: {
    label: 'Ganadora',
    dotClass: 'bg-prize',
    cellClass: 'border-border/60 bg-prize/10 cursor-not-allowed',
    selectable: false,
  },
  cancelled: {
    label: 'No disponible',
    dotClass: 'bg-text-muted',
    cellClass: 'border-border/60 cursor-not-allowed opacity-60',
    selectable: false,
  },
};

export type PublicTicketFilter = 'all' | 'available' | 'reserved' | 'paid';
