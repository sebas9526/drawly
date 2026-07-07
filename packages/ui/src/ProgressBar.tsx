import { cn } from '@drawly/utils';

import { TONE_SOLID, type Tone } from './tones';

interface ProgressBarProps {
  /** 0-100. Values outside that range are clamped. */
  value: number;
  label?: string;
  tone?: Tone;
  size?: 'sm' | 'md';
  className?: string;
}

/** Thin, token-colored progress bar with an optional label + percentage. */
export function ProgressBar({
  value,
  label,
  tone = 'primary',
  size = 'md',
  className,
}: ProgressBarProps): React.JSX.Element {
  const clamped = Math.min(100, Math.max(0, value));

  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      {label && (
        <div className="flex items-center justify-between text-xs">
          <span className="text-text-secondary">{label}</span>
          <span className="text-text-primary font-medium">{Math.round(clamped)}%</span>
        </div>
      )}
      <div
        role="progressbar"
        aria-valuenow={Math.round(clamped)}
        aria-valuemin={0}
        aria-valuemax={100}
        className={cn(
          'bg-muted w-full overflow-hidden rounded-full',
          size === 'sm' ? 'h-1.5' : 'h-2',
        )}
      >
        <div
          className={cn(
            'h-full rounded-full transition-[width] duration-500 ease-out',
            TONE_SOLID[tone],
          )}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
