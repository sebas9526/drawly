import { EmptyState } from './EmptyState';

export interface DonutSegment {
  key: string;
  label: string;
  value: number;
  color: string;
}

interface DonutChartProps {
  segments: DonutSegment[];
  emptyTitle?: string;
  emptyDescription?: string;
  ariaLabel?: string;
}

const RADIUS = 60;
const STROKE = 18;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

/**
 * Generic donut chart, drawn with plain SVG (no charting library — see
 * docs/05-design-system). Segments already carry their own color (usually
 * `TONE_CHART_COLOR[tone]` from `./tones`) so this component stays domain-agnostic.
 */
export function DonutChart({
  segments,
  emptyTitle = 'Sin datos',
  emptyDescription,
  ariaLabel = 'Distribución',
}: DonutChartProps): React.JSX.Element {
  const total = segments.reduce((sum, segment) => sum + segment.value, 0);

  if (total === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  let offset = 0;
  const arcs = segments.map((segment) => {
    const length = (segment.value / total) * CIRCUMFERENCE;
    const arc = { ...segment, length, dashOffset: -offset };
    offset += length;
    return arc;
  });

  return (
    <div className="flex flex-col items-center gap-3">
      <svg viewBox="0 0 160 160" className="h-40 w-40 -rotate-90" role="img" aria-label={ariaLabel}>
        <circle
          cx="80"
          cy="80"
          r={RADIUS}
          fill="none"
          strokeWidth={STROKE}
          className="text-border/40"
          stroke="currentColor"
        />
        {arcs.map((arc) => (
          <circle
            key={arc.key}
            cx="80"
            cy="80"
            r={RADIUS}
            fill="none"
            strokeWidth={STROKE}
            stroke={arc.color}
            strokeDasharray={`${arc.length} ${CIRCUMFERENCE - arc.length}`}
            strokeDashoffset={arc.dashOffset}
          />
        ))}
      </svg>
      <div className="flex flex-wrap justify-center gap-4 text-xs">
        {segments.map((segment) => (
          <span key={segment.key} className="text-text-secondary flex items-center gap-1.5">
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: segment.color }}
              aria-hidden
            />
            {segment.label}: {segment.value}
          </span>
        ))}
      </div>
    </div>
  );
}
