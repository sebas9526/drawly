import { describe, expect, it, vi } from 'vitest';

import { ApiClient } from './fetcher';

function mockFetch(response: unknown, status = 200): typeof fetch {
  return vi.fn().mockResolvedValue({
    status,
    json: async () => response,
  }) as unknown as typeof fetch;
}

describe('ApiClient', () => {
  it('returns data on a successful envelope', async () => {
    const fetchImpl = mockFetch({ success: true, message: 'ok', data: { id: '1' } });
    const client = new ApiClient({ baseUrl: 'http://api.test', fetch: fetchImpl });

    await expect(client.get('/raffles/1')).resolves.toEqual({ id: '1' });
  });

  it('throws ApiError on a failure envelope', async () => {
    const fetchImpl = mockFetch({ success: false, message: 'Not found.', errors: [] }, 404);
    const client = new ApiClient({ baseUrl: 'http://api.test', fetch: fetchImpl });

    await expect(client.get('/raffles/missing')).rejects.toMatchObject({
      name: 'ApiError',
      status: 404,
      message: 'Not found.',
    });
  });

  it('attaches the bearer token from getToken when not skipped', async () => {
    const fetchImpl = mockFetch({ success: true, message: 'ok', data: {} });
    const client = new ApiClient({
      baseUrl: 'http://api.test',
      fetch: fetchImpl,
      getToken: () => 'secret-token',
    });

    await client.get('/participants');

    const [, init] = (fetchImpl as ReturnType<typeof vi.fn>).mock.calls[0] as [string, RequestInit];
    expect((init.headers as Record<string, string>).Authorization).toBe('Bearer secret-token');
  });

  it('calls onUnauthorized when the server responds 401', async () => {
    const fetchImpl = mockFetch({ success: false, message: 'Unauthorized.', errors: [] }, 401);
    const onUnauthorized = vi.fn();
    const client = new ApiClient({ baseUrl: 'http://api.test', fetch: fetchImpl, onUnauthorized });

    await expect(client.get('/dashboard')).rejects.toThrow();
    expect(onUnauthorized).toHaveBeenCalledOnce();
  });
});
