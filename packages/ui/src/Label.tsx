import { cn } from '@drawly/utils';

export function Label({
  className,
  ...props
}: React.LabelHTMLAttributes<HTMLLabelElement>): React.JSX.Element {
  return <label className={cn('text-text-primary text-sm font-medium', className)} {...props} />;
}
