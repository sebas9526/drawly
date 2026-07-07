'use client';

import { DonutChart } from '@drawly/ui/DonutChart';
import { TONE_CHART_COLOR } from '@drawly/ui/tones';

interface TicketDistributionChartProps {
  available: number;
  reserved: number;
  paid: number;
}

/** Ticket distribution donut for the Sprint-7 operational dashboard — a thin
 * wrapper over the generic `DonutChart` (see `@drawly/ui/DonutChart`), reused
 * as-is by the Sprint-9 analytics status distribution chart. */
export function TicketDistributionChart({
  available,
  reserved,
  paid,
}: TicketDistributionChartProps): React.JSX.Element {
  return (
    <DonutChart
      ariaLabel="Distribución de boletas"
      emptyTitle="Sin boletas"
      emptyDescription="Aún no hay boletas generadas."
      segments={[
        {
          key: 'available',
          label: 'Disponibles',
          value: available,
          color: TONE_CHART_COLOR.success,
        },
        { key: 'reserved', label: 'Reservadas', value: reserved, color: TONE_CHART_COLOR.warning },
        { key: 'paid', label: 'Pagadas', value: paid, color: TONE_CHART_COLOR.info },
      ]}
    />
  );
}
