'use client';

import { cn } from '@drawly/utils';

export interface FilterTabOption<T extends string> {
  value: T;
  label: string;
  count?: number;
}

interface FilterTabsProps<T extends string> {
  value: T;
  onChange: (value: T) => void;
  options: FilterTabOption<T>[];
  'aria-label': string;
}

/** Pill-style single-select filter row (e.g. Todas / Disponibles / Reservadas). */
export function FilterTabs<T extends string>({
  value,
  onChange,
  options,
  'aria-label': ariaLabel,
}: FilterTabsProps<T>): React.JSX.Element {
  return (
    <div role="tablist" aria-label={ariaLabel} className="flex flex-wrap gap-1.5">
      {options.map((option) => {
        const active = option.value === value;
        return (
          <button
            key={option.value}
            type="button"
            role="tab"
            aria-selected={active}
            onClick={() => onChange(option.value)}
            className={cn(
              'inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium transition-colors',
              active
                ? 'bg-primary text-primary-fg'
                : 'bg-muted text-text-secondary hover:bg-border hover:text-text-primary',
            )}
          >
            {option.label}
            {option.count !== undefined && (
              <span
                className={cn(
                  'rounded-full px-1.5 text-xs',
                  active ? 'bg-primary-fg/20' : 'bg-border/70',
                )}
              >
                {option.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
