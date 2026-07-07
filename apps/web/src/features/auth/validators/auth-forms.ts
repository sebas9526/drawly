import { z } from 'zod';

/**
 * Client-side auth validation. The backend re-validates everything (Pydantic +
 * Argon2); this only improves UX. Password length mirrors the backend minimum.
 */
export const loginFormSchema = z.object({
  email: z.string().min(1, 'El correo es obligatorio').email('Correo no válido'),
  password: z.string().min(1, 'La contraseña es obligatoria'),
});

export const registerFormSchema = z.object({
  full_name: z.string().min(1, 'El nombre es obligatorio').max(150),
  email: z.string().min(1, 'El correo es obligatorio').email('Correo no válido'),
  password: z.string().min(8, 'Mínimo 8 caracteres').max(128),
});

export interface LoginFormValues {
  email: string;
  password: string;
}

export interface RegisterFormValues {
  full_name: string;
  email: string;
  password: string;
}
