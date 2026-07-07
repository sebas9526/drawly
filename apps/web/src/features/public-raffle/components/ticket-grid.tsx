'use client';

import type { PublicTicketView } from '@drawly/api-client';
import { SearchInput } from '@drawly/ui/SearchInput';
import { cn, formatTicketNumber } from '@drawly/utils';

import { PUBLIC_TICKET_STATUS, type PublicTicketFilter } from '../services/ticket-status';

interface TicketGridProps {
  tickets: PublicTicketView[];
  total: number;
  loading: boolean;
  filter: PublicTicketFilter;
  search: string;
  onFilter: (filter: PublicTicketFilter) => void;
  onSearch: (search: string) => void;
  onSelect: (ticketNumber: number) => void;
}

const FILTERS: { value: PublicTicketFilter; label: string }[] = [
  { value: 'all', label: 'Todas' },
  { value: 'available', label: 'Disponibles' },
  { value: 'reserved', label: 'Reservadas' },
  { value: 'paid', label: 'Pagadas' },
];

export function TicketGrid({
  tickets,
  total,
  loading,
  filter,
  search,
  onFilter,
  onSearch,
  onSelect,
}: TicketGridProps): React.JSX.Element {
  const term = search.trim();
  const visible = tickets.filter((ticket) => {
    const matchesFilter = filter === 'all' || ticket.status === filter;
    const matchesSearch = term === '' || String(ticket.number).includes(term);
    return matchesFilter && matchesSearch;
  });

  return (
    <section className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="bg-muted flex flex-wrap gap-1 rounded-lg p-1">
          {FILTERS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => onFilter(option.value)}
              className={cn(
                'rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
                filter === option.value
                  ? 'bg-surface text-text-primary shadow-sm'
                  : 'text-text-secondary hover:text-text-primary',
              )}
            >
              {option.label}
            </button>
          ))}
        </div>
        <SearchInput
          containerClassName="w-40"
          placeholder="Nº"
          inputMode="numeric"
          value={search}
          onChange={(event) => onSearch(event.target.value)}
        />
      </div>

      <div className="flex flex-wrap gap-4 text-xs">
        {(['available', 'reserved', 'paid', 'cancelled'] as const).map((status) => (
          <span key={status} className="text-text-secondary flex items-center gap-1.5">
            <span
              className={cn(
                'inline-block h-2.5 w-2.5 rounded-full',
                PUBLIC_TICKET_STATUS[status].dotClass,
              )}
            />
            {PUBLIC_TICKET_STATUS[status].label}
          </span>
        ))}
      </div>

      {loading && tickets.length === 0 ? (
        <p className="text-text-secondary text-sm">Cargando boletas…</p>
      ) : visible.length === 0 ? (
        <p className="text-text-secondary text-sm">No hay boletas para este filtro.</p>
      ) : (
        <div className="grid grid-cols-4 gap-2 sm:grid-cols-6 md:grid-cols-8">
          {visible.map((ticket) => {
            const style = PUBLIC_TICKET_STATUS[ticket.status];
            return (
              <button
                key={ticket.number}
                type="button"
                disabled={!style.selectable}
                onClick={() => onSelect(ticket.number)}
                title={style.label}
                className={cn(
                  'flex flex-col items-center gap-1 rounded-lg border px-1 py-2.5 text-xs transition-colors',
                  style.cellClass,
                )}
              >
                <span className={cn('inline-block h-2 w-2 rounded-full', style.dotClass)} />
                <span className="text-text-primary font-mono font-medium">
                  {formatTicketNumber(ticket.number, total)}
                </span>
              </button>
            );
          })}
        </div>
      )}
    </section>
  );
}
