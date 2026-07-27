import { z } from 'zod';

/**
 * Client-side create-raffle validation + coercion. The backend re-validates
 * everything (Pydantic) — this only improves UX. Numbers arrive as strings from
 * the form inputs and are coerced here into the API payload shape.
 */
export const createRaffleFormSchema = z.object({
  title: z.string().min(1, 'El título es obligatorio'),
  prize: z.string().min(1, 'El premio es obligatorio'),
  description: z.string().optional().default(''),
  ticket_price: z.coerce.number().min(0, 'El precio no puede ser negativo'),
  total_tickets: z.coerce
    .number()
    .int('Debe ser un número entero')
    .min(1, 'Debe haber al menos 1 boleta')
    .max(100000, 'Máximo 100000 boletas'),
  starting_number: z.coerce
    .number()
    .int('Debe ser un número entero')
    .refine((value) => value === 0 || value === 1, 'Debe ser 0 o 1'),
  draw_date: z.string().min(1, 'La fecha del sorteo es obligatoria'),
  // Optional: empty means "sin fecha de activación" (publicar manualmente,
  // como hoy). Normalized to undefined here so the request payload omits it
  // entirely instead of sending an empty string.
  publish_at: z
    .string()
    .optional()
    .transform((value) => (value && value.trim() !== '' ? value : undefined)),
});

export interface CreateRaffleFormValues {
  title: string;
  prize: string;
  description: string;
  ticket_price: string;
  total_tickets: string;
  starting_number: string;
  draw_date: string;
  publish_at: string;
}
