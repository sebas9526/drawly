import { cn } from '@drawly/utils';

import { TONE_DOT, TONE_SOFT, type Tone } from './tones';

interface StatusBadgeProps {
  label: string;
  tone?: Tone;
  className?: string;
}

/** Pill with a status dot. Domain maps its status → { label, tone }. */
export function StatusBadge({
  label,
  tone = 'neutral',
  className,
}: StatusBadgeProps): React.JSX.Element {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium',
        TONE_SOFT[tone],
        className,
      )}
    >
      <span className={cn('h-1.5 w-1.5 rounded-full', TONE_DOT[tone])} />
      {label}
    </span>
  );
}
