export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export type QueryParamValue = string | number | boolean | undefined | null;
export type QueryParams = Record<string, QueryParamValue>;

/** Returns the current access token, or null/undefined when unauthenticated. */
export type AuthTokenProvider = () =>
  string | null | undefined | Promise<string | null | undefined>;

export interface ApiClientConfig {
  /** Root API origin, unversioned (e.g. "http://localhost:8000"). */
  baseUrl: string;
  /** Injected per-request if provided. Lets each app own its own token storage. */
  getToken?: AuthTokenProvider;
  /** Called whenever a request fails with 401, after the response is parsed. */
  onUnauthorized?: () => void;
  /** Override for testing or non-global fetch environments. Defaults to global fetch. */
  fetch?: typeof fetch;
  /**
   * fetch credentials mode. Defaults to 'include' so the httpOnly session
   * cookie is sent on cross-origin requests (web <-> api on different ports).
   */
  credentials?: RequestCredentials;
}

export interface RequestOptions {
  query?: QueryParams | undefined;
  headers?: Record<string, string> | undefined;
  /** Skips Authorization header injection for this request (e.g. login). */
  skipAuth?: boolean | undefined;
}
