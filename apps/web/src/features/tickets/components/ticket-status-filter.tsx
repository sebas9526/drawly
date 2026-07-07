'use client';

import { FilterTabs } from '@drawly/ui/FilterTabs';

import type { TicketStatusFilter } from '../validators/ticket-filters';

interface TicketStatusFilterProps {
  value: TicketStatusFilter;
  onChange: (value: TicketStatusFilter) => void;
  counts: { all: number; available: number; reserved: number; paid: number };
}

export function TicketStatusFilterControl({
  value,
  onChange,
  counts,
}: TicketStatusFilterProps): React.JSX.Element {
  return (
    <FilterTabs
      aria-label="Filtrar boletas por estado"
      value={value}
      onChange={onChange}
      options={[
        { value: 'all', label: 'Todas', count: counts.all },
        { value: 'available', label: 'Disponibles', count: counts.available },
        { value: 'reserved', label: 'Reservadas', count: counts.reserved },
        { value: 'paid', label: 'Pagadas', count: counts.paid },
      ]}
    />
  );
}
