import { ChevronDown } from 'lucide-react';
import { forwardRef } from 'react';

import { cn } from '@drawly/utils';

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: boolean;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { className, error, children, ...props },
  ref,
) {
  return (
    <div className="relative">
      <select
        ref={ref}
        className={cn(
          'bg-surface text-text-primary focus:ring-ring/30 h-10 w-full appearance-none rounded-lg border pl-3 pr-9 text-sm transition-colors focus:outline-none focus:ring-2 disabled:opacity-50',
          error ? 'border-danger' : 'border-border focus:border-primary',
          className,
        )}
        {...props}
      >
        {children}
      </select>
      <ChevronDown
        size={16}
        className="text-text-muted pointer-events-none absolute right-3 top-1/2 -translate-y-1/2"
        aria-hidden
      />
    </div>
  );
});
