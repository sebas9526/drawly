import { cn } from '@drawly/utils';

interface AvatarProps {
  name: string;
  size?: 'sm' | 'md';
  className?: string;
}

function initials(name: string): string {
  const parts = name.trim().split(/\s+/).slice(0, 2);
  return parts.map((part) => part[0]?.toUpperCase() ?? '').join('') || '?';
}

const SIZES = { sm: 'h-8 w-8 text-xs', md: 'h-10 w-10 text-sm' };

export function Avatar({ name, size = 'md', className }: AvatarProps): React.JSX.Element {
  return (
    <span
      className={cn(
        'bg-primary/10 text-primary inline-flex shrink-0 items-center justify-center rounded-full font-semibold',
        SIZES[size],
        className,
      )}
      aria-hidden
    >
      {initials(name)}
    </span>
  );
}
