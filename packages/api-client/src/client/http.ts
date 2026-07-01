import type { ApiClientConfig, HttpMethod, RequestOptions } from '../types/config';
import { buildQueryString } from '../utils/query-string';
import { ApiNetworkError } from './errors';
import { withAuthHeader } from './interceptors';

export interface RawRequestInput {
  method: HttpMethod;
  path: string;
  body?: unknown;
  options?: RequestOptions | undefined;
}

/** Performs the actual fetch call: builds the URL, applies interceptors, never throws on non-2xx. */
export async function rawRequest(
  config: ApiClientConfig,
  { method, path, body, options }: RawRequestInput,
): Promise<Response> {
  const fetchImpl = config.fetch ?? globalThis.fetch;
  const url = `${config.baseUrl}${path}${buildQueryString(options?.query)}`;

  let headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options?.headers,
  };

  if (!options?.skipAuth) {
    headers = await withAuthHeader(headers, config.getToken);
  }

  try {
    return await fetchImpl(url, {
      method,
      headers,
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
  } catch (cause) {
    throw new ApiNetworkError(`Failed to reach ${url}.`, cause);
  }
}
