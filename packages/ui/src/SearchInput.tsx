import { Search } from 'lucide-react';

import { cn } from '@drawly/utils';

export interface SearchInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  containerClassName?: string;
}

export function SearchInput({
  className,
  containerClassName,
  ...props
}: SearchInputProps): React.JSX.Element {
  return (
    <div className={cn('relative', containerClassName)}>
      <Search
        size={16}
        className="text-text-muted pointer-events-none absolute left-3 top-1/2 -translate-y-1/2"
        aria-hidden
      />
      <input
        type="search"
        className={cn(
          'border-border bg-surface text-text-primary placeholder:text-text-muted focus:border-primary focus:ring-ring/30 h-10 w-full rounded-lg border pl-9 pr-3 text-sm transition-colors focus:outline-none focus:ring-2',
          className,
        )}
        {...props}
      />
    </div>
  );
}
