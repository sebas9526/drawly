import { z } from 'zod';

/**
 * Generic, domain-agnostic validators reused across entities.
 * No business rules — those belong to each module's own schemas.
 */

export const uuidSchema = z.string().uuid();

export const emailSchema = z.string().email();

export const slugSchema = z
  .string()
  .min(1)
  .max(120)
  .regex(/^[a-z0-9]+(-[a-z0-9]+)*$/, 'Must be lowercase kebab-case');

/** Loose international phone validation (digits, spaces, +, -, parentheses). */
export const phoneSchema = z
  .string()
  .min(7)
  .max(30)
  .regex(/^[0-9+\-() ]+$/, 'Must be a valid phone number');

export const isoDateStringSchema = z.string().datetime({ offset: true }).or(z.string().date());
