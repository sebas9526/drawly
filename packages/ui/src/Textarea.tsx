import { forwardRef } from 'react';

import { cn } from '@drawly/utils';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { className, error, rows = 3, ...props },
  ref,
) {
  return (
    <textarea
      ref={ref}
      rows={rows}
      className={cn(
        'bg-surface text-text-primary placeholder:text-text-muted focus:ring-ring/30 w-full rounded-lg border px-3 py-2 text-sm transition-colors focus:outline-none focus:ring-2 disabled:opacity-50',
        error ? 'border-danger' : 'border-border focus:border-primary',
        className,
      )}
      {...props}
    />
  );
});
