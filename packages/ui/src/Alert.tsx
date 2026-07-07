import { AlertTriangle, CheckCircle2, Info, XCircle } from 'lucide-react';

import { cn } from '@drawly/utils';

type AlertTone = 'info' | 'success' | 'warning' | 'danger';

interface AlertProps {
  tone?: AlertTone;
  title?: string;
  children?: React.ReactNode;
  className?: string;
}

const CONFIG = {
  info: { cls: 'bg-info/10 text-info', Icon: Info },
  success: { cls: 'bg-success/10 text-success', Icon: CheckCircle2 },
  warning: { cls: 'bg-warning/10 text-warning', Icon: AlertTriangle },
  danger: { cls: 'bg-danger/10 text-danger', Icon: XCircle },
} as const;

export function Alert({
  tone = 'info',
  title,
  children,
  className,
}: AlertProps): React.JSX.Element {
  const { cls, Icon } = CONFIG[tone];
  return (
    <div className={cn('flex gap-3 rounded-lg p-3 text-sm', cls, className)} role="alert">
      <Icon size={18} className="mt-0.5 shrink-0" aria-hidden />
      <div className="flex flex-col gap-0.5">
        {title && <p className="font-medium">{title}</p>}
        {children && <div className="opacity-90">{children}</div>}
      </div>
    </div>
  );
}
