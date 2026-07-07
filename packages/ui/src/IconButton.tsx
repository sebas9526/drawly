import { cn } from '@drawly/utils';

type IconButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
type IconButtonSize = 'sm' | 'md';

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: IconButtonVariant;
  size?: IconButtonSize;
  'aria-label': string;
}

const VARIANTS: Record<IconButtonVariant, string> = {
  primary: 'bg-primary text-primary-fg hover:bg-primary-hover',
  secondary: 'bg-muted text-text-primary hover:bg-border',
  outline:
    'border border-border bg-surface text-text-secondary hover:bg-muted hover:text-text-primary',
  ghost: 'text-text-secondary hover:bg-muted hover:text-text-primary',
  danger: 'text-danger hover:bg-danger/10',
};

const SIZES: Record<IconButtonSize, string> = { sm: 'h-8 w-8', md: 'h-10 w-10' };

/** Shared classNames so non-`<button>` triggers (e.g. Dropdown's trigger wrapper)
 * can visually match IconButton without nesting two `<button>` elements. */
export function iconButtonClassName(
  variant: IconButtonVariant = 'ghost',
  size: IconButtonSize = 'md',
  className?: string,
): string {
  return cn(
    'inline-flex items-center justify-center rounded-lg transition-colors',
    'disabled:pointer-events-none disabled:opacity-50',
    VARIANTS[variant],
    SIZES[size],
    className,
  );
}

export function IconButton({
  variant = 'ghost',
  size = 'md',
  className,
  type = 'button',
  children,
  ...props
}: IconButtonProps): React.JSX.Element {
  return (
    <button type={type} className={iconButtonClassName(variant, size, className)} {...props}>
      {children}
    </button>
  );
}
