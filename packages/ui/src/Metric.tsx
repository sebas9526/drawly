interface MetricProps {
  label: string;
  value: React.ReactNode;
  hint?: string;
}

export function Metric({ label, value, hint }: MetricProps): React.JSX.Element {
  return (
    <div className="flex flex-col">
      <span className="text-text-primary text-xl font-semibold">{value}</span>
      <span className="text-text-secondary text-xs">{label}</span>
      {hint && <span className="text-text-muted text-xs">{hint}</span>}
    </div>
  );
}
