import { afterEach, describe, expect, it, vi } from 'vitest';

import { api } from './api';

describe('api', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('wires the shared client with all endpoint groups', () => {
    expect(api.health).toBeDefined();
    expect(api.raffles).toBeDefined();
    expect(api.participants).toBeDefined();
    expect(api.tickets).toBeDefined();
    expect(api.dashboard).toBeDefined();
  });

  it('resolves health.check() against the configured base URL', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      status: 200,
      json: async () => ({ success: true, message: 'ok', data: { status: 'ok' } }),
    });
    vi.stubGlobal('fetch', fetchMock);

    await expect(api.health.check()).resolves.toEqual({ status: 'ok' });
    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/health',
      expect.objectContaining({ method: 'GET' }),
    );
  });
});
