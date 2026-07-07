import { cn } from '@drawly/utils';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

/** Base surface container. Rounded, subtle border + shadow, theme-aware. */
export function Card({ children, className }: CardProps): React.JSX.Element {
  return (
    <div className={cn('bg-card border-border rounded-xl border shadow-sm', className)}>
      {children}
    </div>
  );
}
