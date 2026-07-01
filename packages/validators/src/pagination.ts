import { z } from 'zod';

/**
 * Shared pagination query schema. Mirrors docs/04-api/RESPONSE_FORMAT.md
 * (default page_size: 20) and docs/04-api/API_SPECIFICATION.md list endpoints.
 */
export const paginationQuerySchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  page_size: z.coerce.number().int().min(1).max(100).default(20),
});

export type PaginationQuery = z.infer<typeof paginationQuerySchema>;
