const dayFormatter = new Intl.DateTimeFormat('es-CO', { day: '2-digit', month: 'short' });

/** Formats an ISO date ("2026-01-15") as a short chart-axis label ("15 ene"). */
export function formatChartDay(iso: string): string {
  return dayFormatter.format(new Date(`${iso}T00:00:00`));
}
