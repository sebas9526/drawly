import { emailSchema, phoneSchema } from '@drawly/validators';
import { z } from 'zod';

/** Palette offered in the color picker (matches the design system accents). */
export const COLLABORATOR_COLORS = [
  '#4F46E5',
  '#0EA5E9',
  '#10B981',
  '#F59E0B',
  '#EF4444',
  '#EC4899',
  '#8B5CF6',
  '#14B8A6',
] as const;

const HEX_COLOR = /^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/;

export const collaboratorFormSchema = z.object({
  raffle_id: z.string().min(1, 'Selecciona una rifa'),
  name: z.string().min(1, 'El nombre es obligatorio').max(150),
  phone: phoneSchema.optional().or(z.literal('')),
  email: emailSchema.max(150).optional().or(z.literal('')),
  color: z.string().regex(HEX_COLOR, 'Color no válido'),
  notes: z.string().max(2000).optional().or(z.literal('')),
  is_active: z.boolean(),
});

export interface CollaboratorFormValues {
  raffle_id: string;
  name: string;
  phone: string;
  email: string;
  color: string;
  notes: string;
  is_active: boolean;
}
