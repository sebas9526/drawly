import { createDrawlyApiClient } from '@drawly/api-client';

/**
 * Single shared client instance for the web app.
 * Components/hooks must go through this — never call fetch() directly
 * against the API (see @drawly/api-client's README for why).
 */
export const api = createDrawlyApiClient({
  baseUrl: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
});
