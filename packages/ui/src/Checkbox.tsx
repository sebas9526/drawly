import { forwardRef } from 'react';

import { cn } from '@drawly/utils';

export interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(function Checkbox(
  { className, label, id, ...props },
  ref,
) {
  return (
    <label className="text-text-primary flex items-center gap-2 text-sm">
      <input
        ref={ref}
        id={id}
        type="checkbox"
        className={cn('accent-primary border-border h-4 w-4 rounded', className)}
        {...props}
      />
      {label}
    </label>
  );
});
