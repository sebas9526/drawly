import { emailSchema, phoneSchema } from '@drawly/validators';
import { z } from 'zod';

/** Client-side validation for the public reservation form. The backend
 * re-validates and remains the source of truth. */
export const reserveFormSchema = z.object({
  full_name: z.string().min(1, 'El nombre es obligatorio'),
  phone: phoneSchema,
  email: emailSchema.or(z.literal('')),
  document: z.string(),
  /** Optional collaborator (seller) id. */
  collaborator_id: z.string(),
});

export interface ReserveFormValues {
  full_name: string;
  phone: string;
  email: string;
  document: string;
  collaborator_id: string;
}

export const EMPTY_RESERVE_FORM: ReserveFormValues = {
  full_name: '',
  phone: '',
  email: '',
  document: '',
  collaborator_id: '',
};
