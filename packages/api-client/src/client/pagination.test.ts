import { describe, expect, it, vi } from 'vitest';

import { fetchAllPages } from './pagination';
import type { PaginatedResult } from './response';

function page(
  data: number[],
  pageNumber: number,
  pageSize: number,
  total: number,
): PaginatedResult<number> {
  return {
    data,
    pagination: {
      page: pageNumber,
      page_size: pageSize,
      total,
      total_pages: Math.ceil(total / pageSize),
    },
  };
}

describe('fetchAllPages', () => {
  it('returns everything in one call when it all fits on the first page', async () => {
    const fetchPage = vi.fn().mockResolvedValue(page([1, 2, 3], 1, 200, 3));

    const items = await fetchAllPages(fetchPage);

    expect(items).toEqual([1, 2, 3]);
    expect(fetchPage).toHaveBeenCalledOnce();
  });

  it('concatenates every page in order', async () => {
    const fetchPage = vi
      .fn()
      .mockResolvedValueOnce(page([1, 2], 1, 2, 5))
      .mockResolvedValueOnce(page([3, 4], 2, 2, 5))
      .mockResolvedValueOnce(page([5], 3, 2, 5));

    const items = await fetchAllPages(fetchPage, 2);

    expect(items).toEqual([1, 2, 3, 4, 5]);
    expect(fetchPage).toHaveBeenCalledTimes(3);
    expect(fetchPage).toHaveBeenNthCalledWith(1, 1, 2);
    expect(fetchPage).toHaveBeenNthCalledWith(2, 2, 2);
    expect(fetchPage).toHaveBeenNthCalledWith(3, 3, 2);
  });

  it('returns an empty array when there is nothing to fetch', async () => {
    const fetchPage = vi.fn().mockResolvedValue(page([], 1, 200, 0));

    const items = await fetchAllPages(fetchPage);

    expect(items).toEqual([]);
    expect(fetchPage).toHaveBeenCalledOnce();
  });
});
