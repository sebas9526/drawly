/**
 * Shared API envelope contract.
 * Mirrors docs/04-api/RESPONSE_FORMAT.md and docs/04-api/ERROR_HANDLING.md.
 * Every Drawly endpoint must respond using one of these shapes.
 */

export interface ApiSuccessResponse<TData> {
  success: true;
  message: string;
  data: TData;
}

export interface ApiFieldError {
  field: string;
  message: string;
}

export interface ApiErrorResponse {
  success: false;
  message: string;
  errors: ApiFieldError[];
  trace_id?: string;
}

export type ApiResponse<TData> = ApiSuccessResponse<TData> | ApiErrorResponse;

/** Mirrors app/core/responses.py::PaginationMeta (wire format, snake_case). */
export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface PaginatedResponse<TItem> {
  success: true;
  data: TItem[];
  pagination: PaginationMeta;
}
