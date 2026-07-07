import { Card } from './Card';

interface MetricCardProps {
  label: string;
  value: React.ReactNode;
  hint?: string;
  icon?: React.ReactNode;
}

export function MetricCard({ label, value, hint, icon }: MetricCardProps): React.JSX.Element {
  return (
    <Card className="flex flex-col gap-1 p-5">
      <div className="text-text-secondary flex items-center justify-between text-xs font-medium uppercase tracking-wide">
        {label}
        {icon && <span className="text-text-muted">{icon}</span>}
      </div>
      <span className="text-text-primary text-2xl font-semibold">{value}</span>
      {hint && <span className="text-text-muted text-xs">{hint}</span>}
    </Card>
  );
}
