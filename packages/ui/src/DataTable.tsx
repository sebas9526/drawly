'use client';

import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react';
import { useMemo, useState } from 'react';

import { cn } from '@drawly/utils';

import { Checkbox } from './Checkbox';
import { Pagination } from './Pagination';
import { Skeleton } from './Skeleton';

export interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => React.ReactNode;
  className?: string;
  sortable?: boolean;
  sortValue?: (row: T) => string | number;
}

export interface DataTableSelection {
  selectedKeys: Set<string>;
  onToggle: (key: string) => void;
  onToggleAll: (keys: string[]) => void;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  getRowKey: (row: T, index: number) => string;
  loading?: boolean;
  empty?: React.ReactNode;
  pageSize?: number;
  /** Enables a checkbox column for multi-row selection (bulk actions). */
  selection?: DataTableSelection;
}

type SortState = { key: string; dir: 'asc' | 'desc' } | null;

export function DataTable<T>({
  columns,
  rows,
  getRowKey,
  loading = false,
  empty,
  pageSize,
  selection,
}: DataTableProps<T>): React.JSX.Element {
  const [sort, setSort] = useState<SortState>(null);
  const [page, setPage] = useState(1);

  const sorted = useMemo(() => {
    if (!sort) return rows;
    const column = columns.find((candidate) => candidate.key === sort.key);
    const sortValue = column?.sortValue;
    if (!sortValue) return rows;
    const factor = sort.dir === 'asc' ? 1 : -1;
    return [...rows].sort((a, b) => {
      const av = sortValue(a);
      const bv = sortValue(b);
      if (typeof av === 'number' && typeof bv === 'number') return (av - bv) * factor;
      return String(av).localeCompare(String(bv)) * factor;
    });
  }, [rows, sort, columns]);

  const pageCount = pageSize ? Math.ceil(sorted.length / pageSize) : 1;
  const current = Math.min(page, Math.max(pageCount, 1));
  const visible = pageSize ? sorted.slice((current - 1) * pageSize, current * pageSize) : sorted;

  const toggleSort = (key: string): void => {
    setSort((prev) =>
      prev?.key === key ? { key, dir: prev.dir === 'asc' ? 'desc' : 'asc' } : { key, dir: 'asc' },
    );
  };

  if (loading) {
    return (
      <div className="flex flex-col gap-2">
        {Array.from({ length: 4 }).map((_, index) => (
          <Skeleton key={index} className="h-9 w-full" />
        ))}
      </div>
    );
  }

  if (sorted.length === 0) {
    return <>{empty ?? <p className="text-text-secondary py-6 text-sm">Sin datos.</p>}</>;
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-sm">
          <thead>
            <tr className="text-text-secondary border-border border-b">
              {selection && (
                <th className="w-10 py-2.5 pr-2">
                  <Checkbox
                    aria-label="Seleccionar todo"
                    checked={
                      visible.length > 0 &&
                      visible.every((row, index) =>
                        selection.selectedKeys.has(getRowKey(row, index)),
                      )
                    }
                    onChange={() =>
                      selection.onToggleAll(visible.map((row, index) => getRowKey(row, index)))
                    }
                  />
                </th>
              )}
              {columns.map((column) => (
                <th key={column.key} className={cn('py-2.5 pr-4 font-medium', column.className)}>
                  {column.sortable ? (
                    <button
                      type="button"
                      onClick={() => toggleSort(column.key)}
                      className="hover:text-text-primary inline-flex items-center gap-1 transition-colors"
                    >
                      {column.header}
                      {sort?.key === column.key ? (
                        sort.dir === 'asc' ? (
                          <ArrowUp size={12} />
                        ) : (
                          <ArrowDown size={12} />
                        )
                      ) : (
                        <ArrowUpDown size={12} className="opacity-50" />
                      )}
                    </button>
                  ) : (
                    column.header
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visible.map((row, index) => {
              const rowKey = getRowKey(row, index);
              return (
                <tr
                  key={rowKey}
                  className="border-border/60 hover:bg-muted/50 border-b transition-colors"
                >
                  {selection && (
                    <td className="py-2.5 pr-2">
                      <Checkbox
                        aria-label="Seleccionar fila"
                        checked={selection.selectedKeys.has(rowKey)}
                        onChange={() => selection.onToggle(rowKey)}
                      />
                    </td>
                  )}
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      className={cn('text-text-primary py-2.5 pr-4', column.className)}
                    >
                      {column.render(row)}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {pageSize && pageCount > 1 && (
        <Pagination page={current} pageCount={pageCount} onPageChange={setPage} />
      )}
    </div>
  );
}
