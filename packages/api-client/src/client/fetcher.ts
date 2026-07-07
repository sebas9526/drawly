import type { ApiClientConfig, RequestOptions } from '../types/config';
import { ApiError } from './errors';
import { rawRequest } from './http';
import { parseApiResponse, parsePaginatedResponse, type PaginatedResult } from './response';

/**
 * Framework-agnostic HTTP client for the Drawly API.
 * Holds no business logic — only request/response plumbing shared by every
 * endpoints/*.ts module (and, eventually, a React Native app).
 */
export class ApiClient {
  constructor(private readonly config: ApiClientConfig) {}

  async get<TData>(path: string, options?: RequestOptions): Promise<TData> {
    return this.send<TData>('GET', path, undefined, options);
  }

  async post<TData>(path: string, body?: unknown, options?: RequestOptions): Promise<TData> {
    return this.send<TData>('POST', path, body, options);
  }

  async put<TData>(path: string, body?: unknown, options?: RequestOptions): Promise<TData> {
    return this.send<TData>('PUT', path, body, options);
  }

  async patch<TData>(path: string, body?: unknown, options?: RequestOptions): Promise<TData> {
    return this.send<TData>('PATCH', path, body, options);
  }

  async delete<TData>(path: string, options?: RequestOptions): Promise<TData> {
    return this.send<TData>('DELETE', path, undefined, options);
  }

  async getPaginated<TItem>(
    path: string,
    options?: RequestOptions,
  ): Promise<PaginatedResult<TItem>> {
    const response = await rawRequest(this.config, { method: 'GET', path, options });
    return this.withUnauthorizedHandling(response, () => parsePaginatedResponse<TItem>(response));
  }

  /** For endpoints that return a raw file (e.g. Excel/PDF exports) instead of
   * the `{success, data}` envelope. */
  async getBlob(path: string, options?: RequestOptions): Promise<Blob> {
    const response = await rawRequest(this.config, { method: 'GET', path, options });
    if (!response.ok) {
      if (response.status === 401) this.config.onUnauthorized?.();
      throw new ApiError(`Failed to download ${path}.`, response.status);
    }
    return response.blob();
  }

  private async send<TData>(
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE',
    path: string,
    body: unknown,
    options?: RequestOptions,
  ): Promise<TData> {
    const response = await rawRequest(this.config, { method, path, body, options });
    return this.withUnauthorizedHandling(response, () => parseApiResponse<TData>(response));
  }

  private async withUnauthorizedHandling<TResult>(
    response: Response,
    parse: () => Promise<TResult>,
  ): Promise<TResult> {
    try {
      return await parse();
    } catch (error) {
      if (response.status === 401) this.config.onUnauthorized?.();
      throw error;
    }
  }
}

export { ApiError, ApiNetworkError, isApiError, isApiNetworkError } from './errors';
export type { PaginatedResult } from './response';
