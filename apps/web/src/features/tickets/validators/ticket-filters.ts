import { z } from 'zod';

/**
 * Frontend filter validation. The backend is still the source of truth for
 * business rules — this only guards UI state. Matches the four quick-filter
 * tabs on the tickets screen (winner/cancelled tickets are rare edge states
 * and remain visible under "Todas").
 */
export const ticketStatusFilterSchema = z.enum(['all', 'available', 'reserved', 'paid']);

export type TicketStatusFilter = z.infer<typeof ticketStatusFilterSchema>;
