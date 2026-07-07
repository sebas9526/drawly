import { cn } from '@drawly/utils';

export function Skeleton({ className }: { className?: string }): React.JSX.Element {
  return <div className={cn('bg-muted animate-pulse rounded-md', className)} aria-hidden />;
}
