import type { ApiResponse, PaginationMeta } from '@drawly/types';

import { ApiError, ApiNetworkError } from './errors';

export interface PaginatedResult<TItem> {
  data: TItem[];
  pagination: PaginationMeta;
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch (cause) {
    throw new ApiNetworkError('Response was not valid JSON.', cause);
  }
}

/** Parses a standard `{success, message, data}` / `{success, message, errors}` envelope. */
export async function parseApiResponse<TData>(response: Response): Promise<TData> {
  const body = (await readJson(response)) as ApiResponse<TData>;

  if (!body.success) {
    throw new ApiError(body.message, response.status, body.errors, body.trace_id);
  }

  return body.data;
}

/** Parses a `{success, data, pagination}` paginated envelope. */
export async function parsePaginatedResponse<TItem>(
  response: Response,
): Promise<PaginatedResult<TItem>> {
  const body = (await readJson(response)) as
    | { success: true; data: TItem[]; pagination: PaginationMeta }
    | { success: false; message: string; errors?: never };

  if (!body.success) {
    throw new ApiError(body.message, response.status);
  }

  return { data: body.data, pagination: body.pagination };
}
