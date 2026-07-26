import type { PaginatedResult } from './response';

const DEFAULT_PAGE_SIZE = 200;
// Hard safety ceiling: at DEFAULT_PAGE_SIZE this covers 100,000 rows (the
// platform's own max, e.g. total_tickets) without ever looping unbounded if
// `total` were ever wrong.
const MAX_PAGES = 500;

/**
 * Fetches every page of a paginated endpoint and concatenates the results.
 *
 * Some admin views still expect the *complete* list client-side (e.g. ticket
 * search/filter/bulk-select across a whole raffle) even though the backend
 * must stay bounded per request rather than accept one unbounded page_size.
 * This keeps that UX unchanged while every individual request stays capped.
 */
export async function fetchAllPages<TItem>(
  fetchPage: (page: number, pageSize: number) => Promise<PaginatedResult<TItem>>,
  pageSize: number = DEFAULT_PAGE_SIZE,
): Promise<TItem[]> {
  const first = await fetchPage(1, pageSize);
  const items = [...first.data];
  const totalPages = Math.min(first.pagination.total_pages, MAX_PAGES);

  for (let page = 2; page <= totalPages; page += 1) {
    const next = await fetchPage(page, pageSize);
    items.push(...next.data);
  }

  return items;
}
