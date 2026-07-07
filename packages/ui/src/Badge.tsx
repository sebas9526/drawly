import { cn } from '@drawly/utils';

import { TONE_SOFT, type Tone } from './tones';

interface BadgeProps {
  tone?: Tone;
  children: React.ReactNode;
  className?: string;
}

export function Badge({ tone = 'neutral', children, className }: BadgeProps): React.JSX.Element {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        TONE_SOFT[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
