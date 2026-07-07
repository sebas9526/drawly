import { cn } from '@drawly/utils';

import { Card } from './Card';

interface DashboardCardProps {
  title?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export function DashboardCard({
  title,
  action,
  children,
  className,
}: DashboardCardProps): React.JSX.Element {
  return (
    <Card className={cn('flex flex-col gap-4 p-5', className)}>
      {(title || action) && (
        <div className="flex items-center justify-between">
          {title && <h3 className="text-text-primary text-sm font-semibold">{title}</h3>}
          {action}
        </div>
      )}
      {children}
    </Card>
  );
}
