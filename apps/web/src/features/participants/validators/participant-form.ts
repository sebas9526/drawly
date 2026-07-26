import { emailSchema, phoneSchema } from '@drawly/validators';
import { z } from 'zod';

/**
 * Client-side participant form validation. The backend re-validates everything;
 * this only improves UX. Optional fields accept empty strings (mapped to
 * undefined before sending).
 */
export const participantFormSchema = z.object({
  full_name: z.string().min(1, 'El nombre es obligatorio'),
  phone: phoneSchema,
  email: emailSchema.or(z.literal('')),
  document: z.string(),
  city: z.string(),
  address: z.string(),
  notes: z.string(),
});

export interface ParticipantFormValues {
  full_name: string;
  phone: string;
  email: string;
  document: string;
  city: string;
  address: string;
  notes: string;
}

export const EMPTY_PARTICIPANT_FORM: ParticipantFormValues = {
  full_name: '',
  phone: '',
  email: '',
  document: '',
  city: '',
  address: '',
  notes: '',
};
