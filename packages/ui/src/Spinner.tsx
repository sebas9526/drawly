import { Loader2 } from 'lucide-react';

import { cn } from '@drawly/utils';

interface SpinnerProps {
  size?: number;
  className?: string;
}

export function Spinner({ size = 16, className }: SpinnerProps): React.JSX.Element {
  return <Loader2 size={size} className={cn('animate-spin', className)} aria-hidden />;
}
