import { forwardRef } from 'react';

import { cn } from '@drawly/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
}

const BASE =
  'h-10 w-full rounded-lg border bg-surface px-3 text-sm text-text-primary placeholder:text-text-muted transition-colors focus:outline-none focus:ring-2 focus:ring-ring/30 disabled:opacity-50';

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { className, error, ...props },
  ref,
) {
  return (
    <input
      ref={ref}
      className={cn(
        BASE,
        error ? 'border-danger' : 'border-border focus:border-primary',
        className,
      )}
      {...props}
    />
  );
});
