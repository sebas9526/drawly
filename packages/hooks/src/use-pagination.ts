import { useCallback, useState } from 'react';

export interface UsePaginationOptions {
  initialPage?: number;
  initialPageSize?: number;
}

export interface UsePaginationResult {
  page: number;
  pageSize: number;
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  nextPage: () => void;
  previousPage: () => void;
}

/** Generic page/pageSize state manager. Does not fetch data itself. */
export function usePagination(options: UsePaginationOptions = {}): UsePaginationResult {
  const { initialPage = 1, initialPageSize = 20 } = options;

  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);

  const nextPage = useCallback(() => setPage((current) => current + 1), []);
  const previousPage = useCallback(() => setPage((current) => Math.max(1, current - 1)), []);

  return { page, pageSize, setPage, setPageSize, nextPage, previousPage };
}
