import { emailSchema, phoneSchema } from '@drawly/validators';
import { z } from 'zod';

/** Palette offered in the color picker — the -600 shade of each design-system
 * accent (primary, info, success, prize, danger) plus three extra accents
 * for variety beyond the semantic tones. A collaborator's stored `color` is
 * always a plain hex string (Collaborator.color), independent of these
 * tokens — existing collaborators keep whatever hex they already have, this
 * array only affects the picker shown when choosing/changing a color. */
export const COLLABORATOR_COLORS = [
  '#5B3FDB', // primary-600
  '#0284C7', // info-600
  '#059669', // success-600
  '#A66F10', // prize-600
  '#DC2626', // danger-600
  '#DB2777', // pink-600 (extra accent)
  '#7C3AED', // violet-600 (extra accent)
  '#0D9488', // teal-600 (extra accent)
] as const;

const HEX_COLOR = /^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/;

export const collaboratorFormSchema = z.object({
  raffle_ids: z.array(z.string()).min(1, 'Selecciona al menos una rifa'),
  name: z.string().min(1, 'El nombre es obligatorio').max(150),
  phone: phoneSchema.optional().or(z.literal('')),
  email: emailSchema.max(150).optional().or(z.literal('')),
  color: z.string().regex(HEX_COLOR, 'Color no válido'),
  notes: z.string().max(2000).optional().or(z.literal('')),
  is_active: z.boolean(),
});

export interface CollaboratorFormValues {
  raffle_ids: string[];
  name: string;
  phone: string;
  email: string;
  color: string;
  notes: string;
  is_active: boolean;
}
