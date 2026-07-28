import { AlertTriangle, CheckCircle2, Info, XCircle } from 'lucide-react';

import { cn } from '@drawly/utils';

import { TONE_SOFT, type Tone } from './tones';

type AlertTone = Extract<Tone, 'info' | 'success' | 'warning' | 'danger'>;

interface AlertProps {
  tone?: AlertTone;
  title?: string;
  children?: React.ReactNode;
  className?: string;
}

// Reuses TONE_SOFT (./tones) for color so Alert can't drift from
// Badge/StatusBadge/StatCard — only the icon mapping is Alert's own.
const ICONS: Record<AlertTone, typeof Info> = {
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  danger: XCircle,
};

export function Alert({
  tone = 'info',
  title,
  children,
  className,
}: AlertProps): React.JSX.Element {
  const Icon = ICONS[tone];
  return (
    <div
      className={cn('flex gap-3 rounded-lg p-3 text-sm', TONE_SOFT[tone], className)}
      role="alert"
    >
      <Icon size={18} className="mt-0.5 shrink-0" aria-hidden />
      <div className="flex flex-col gap-0.5">
        {title && <p className="font-medium">{title}</p>}
        {children && <div className="opacity-90">{children}</div>}
      </div>
    </div>
  );
}
