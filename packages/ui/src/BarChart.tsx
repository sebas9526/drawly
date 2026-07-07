import { EmptyState } from './EmptyState';

export interface BarDatum {
  label: string;
  value: number;
}

interface BarChartProps {
  data: BarDatum[];
  color?: string;
  formatValue?: (value: number) => string;
  orientation?: 'vertical' | 'horizontal';
  emptyTitle?: string;
  emptyDescription?: string;
}

/**
 * Generic single-series bar chart (no charting library). `vertical` reads as
 * a small time series (day-by-day); `horizontal` reads as a ranked list
 * (Top-N). One hue only — magnitude, not identity — per the project's chart
 * color rule (see `TONE_CHART_COLOR` in `./tones`).
 */
export function BarChart({
  data,
  color = 'rgb(var(--color-primary))',
  formatValue,
  orientation = 'vertical',
  emptyTitle = 'Sin datos',
  emptyDescription,
}: BarChartProps): React.JSX.Element {
  if (data.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  const max = Math.max(...data.map((datum) => datum.value), 1);
  const display = (value: number): string => (formatValue ? formatValue(value) : String(value));

  if (orientation === 'horizontal') {
    return (
      <div className="flex flex-col gap-2.5" role="img" aria-label="Ranking">
        {data.map((datum) => (
          <div key={datum.label} className="flex items-center gap-3">
            <span className="text-text-secondary w-28 shrink-0 truncate text-xs">
              {datum.label}
            </span>
            <div className="bg-muted h-2.5 flex-1 overflow-hidden rounded-full">
              <div
                className="h-full rounded-full transition-[width] duration-500 ease-out"
                style={{ width: `${(datum.value / max) * 100}%`, backgroundColor: color }}
              />
            </div>
            <span className="text-text-primary w-20 shrink-0 text-right text-xs font-medium tabular-nums">
              {display(datum.value)}
            </span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="flex h-40 items-end gap-1.5" role="img" aria-label="Serie de tiempo">
      {data.map((datum) => (
        <div
          key={datum.label}
          className="group relative flex flex-1 flex-col items-center justify-end gap-1"
        >
          <span className="text-text-primary pointer-events-none absolute -top-5 hidden text-[10px] font-medium tabular-nums group-hover:block">
            {display(datum.value)}
          </span>
          <div
            className="w-full min-w-[3px] rounded-t-sm"
            style={{
              height: datum.value > 0 ? `${Math.max((datum.value / max) * 100, 3)}%` : '2px',
              backgroundColor: datum.value > 0 ? color : 'rgb(var(--color-border))',
            }}
          />
          <span className="text-text-muted w-full truncate text-center text-[10px]">
            {datum.label}
          </span>
        </div>
      ))}
    </div>
  );
}
