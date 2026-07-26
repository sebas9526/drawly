import { z } from 'zod';

/**
 * Generic, domain-agnostic validators reused across entities.
 * No business rules — those belong to each module's own schemas.
 */

export const uuidSchema = z.string().uuid();

// Messages are Spanish — every Drawly surface that uses this package is
// Spanish-locale (see docs/04-api and the admin/public UI copy); a shared
// validator is the single place this only needs saying once.
export const emailSchema = z.string().email('Correo no válido');

export const slugSchema = z
  .string()
  .min(1)
  .max(120)
  .regex(/^[a-z0-9]+(-[a-z0-9]+)*$/, 'Debe ser kebab-case en minúsculas');

/** Loose international phone validation (digits, spaces, +, -, parentheses). */
export const phoneSchema = z
  .string()
  .min(7, 'Debe tener al menos 7 dígitos')
  .max(30, 'Máximo 30 caracteres')
  .regex(/^[0-9+\-() ]+$/, 'Debe ser un teléfono válido');

export const isoDateStringSchema = z.string().datetime({ offset: true }).or(z.string().date());
