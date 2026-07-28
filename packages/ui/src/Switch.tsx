import { cn } from '@drawly/utils';

interface SwitchProps {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  disabled?: boolean;
  'aria-label'?: string;
  id?: string;
}

export function Switch({
  checked,
  onCheckedChange,
  disabled,
  id,
  'aria-label': ariaLabel,
}: SwitchProps): React.JSX.Element {
  return (
    <button
      type="button"
      role="switch"
      id={id}
      aria-checked={checked}
      aria-label={ariaLabel}
      disabled={disabled}
      onClick={() => onCheckedChange(!checked)}
      className={cn(
        'relative inline-flex h-6 w-11 items-center rounded-full transition-colors disabled:opacity-50',
        checked ? 'bg-primary' : 'bg-border',
      )}
    >
      <span
        className={cn(
          // A pure background-color match to the track (e.g. white-on-white
          // in light mode) gave near-zero edge contrast — the ring gives the
          // thumb a visible boundary regardless of theme or state.
          'ring-border-strong bg-surface inline-block h-5 w-5 transform rounded-full shadow ring-1 transition-transform',
          checked ? 'translate-x-5' : 'translate-x-0.5',
        )}
      />
    </button>
  );
}
