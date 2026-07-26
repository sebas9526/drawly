import type { ApiFieldError } from '@drawly/types';

/** Thrown when the server responded with a standard error envelope (success: false). */
export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly errors: ApiFieldError[] = [],
    public readonly traceId?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/** Thrown when the request never reached the server, or the response wasn't valid JSON. */
export class ApiNetworkError extends Error {
  constructor(
    message: string,
    public override readonly cause?: unknown,
  ) {
    super(message);
    this.name = 'ApiNetworkError';
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export function isApiNetworkError(error: unknown): error is ApiNetworkError {
  return error instanceof ApiNetworkError;
}

/** The single place `isApiError(error) ? error.message : fallback` gets
 * written, instead of repeating the ternary at every mutation call site. */
export function getApiErrorMessage(error: unknown, fallback: string): string {
  return isApiError(error) ? error.message : fallback;
}
