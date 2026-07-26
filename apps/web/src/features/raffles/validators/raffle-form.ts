import { z } from 'zod';

/**
 * Client-side create-raffle validation + coercion. The backend re-validates
 * everything (Pydantic) — this only improves UX. Numbers arrive as strings from
 * the form inputs and are coerced here into the API payload shape.
 */
export const createRaffleFormSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  prize: z.string().min(1, 'Prize is required'),
  description: z.string().optional().default(''),
  ticket_price: z.coerce.number().min(0, 'Price cannot be negative'),
  total_tickets: z.coerce
    .number()
    .int('Must be a whole number')
    .min(1, 'At least 1 ticket')
    .max(100000, 'At most 100000 tickets'),
  starting_number: z.coerce
    .number()
    .int('Must be a whole number')
    .refine((value) => value === 0 || value === 1, 'Must be 0 or 1'),
  draw_date: z.string().min(1, 'Draw date is required'),
});

export interface CreateRaffleFormValues {
  title: string;
  prize: string;
  description: string;
  ticket_price: string;
  total_tickets: string;
  starting_number: string;
  draw_date: string;
}
