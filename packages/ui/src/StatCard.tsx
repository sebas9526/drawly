import { cn } from '@drawly/utils';

import { Card } from './Card';
import { TONE_SOFT, type Tone } from './tones';

interface StatCardProps {
  label: string;
  value: React.ReactNode;
  hint?: string;
  icon?: React.ReactNode;
  tone?: Tone;
  /** When set, the whole card becomes a link (keyboard-focusable, hover lift). */
  href?: string;
  className?: string;
}

export function StatCard({
  label,
  value,
  hint,
  icon,
  tone = 'primary',
  href,
  className,
}: StatCardProps): React.JSX.Element {
  const content = (
    <Card
      className={cn(
        'flex items-center gap-4 p-5',
        href &&
          'hover:border-primary/40 focus-visible:ring-ring transition-all hover:-translate-y-0.5 hover:shadow-md focus-visible:outline-none focus-visible:ring-2',
        className,
      )}
    >
      {icon && (
        <span
          className={cn(
            'flex h-11 w-11 shrink-0 items-center justify-center rounded-lg',
            TONE_SOFT[tone],
          )}
        >
          {icon}
        </span>
      )}
      <div className="flex flex-col">
        <span className="text-text-secondary text-xs font-medium uppercase tracking-wide">
          {label}
        </span>
        <span className="text-text-primary text-2xl font-semibold">{value}</span>
        {hint && <span className="text-text-muted text-xs">{hint}</span>}
      </div>
    </Card>
  );

  if (!href) return content;

  return (
    <a href={href} className="block rounded-xl">
      {content}
    </a>
  );
}
