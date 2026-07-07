interface EmptyStateProps {
  title: string;
  description?: string | undefined;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export function EmptyState({
  title,
  description,
  icon,
  action,
}: EmptyStateProps): React.JSX.Element {
  return (
    <div className="border-border/70 flex flex-col items-center gap-2 rounded-xl border border-dashed p-8 text-center">
      {icon && <div className="text-text-muted">{icon}</div>}
      <p className="text-text-primary text-sm font-medium">{title}</p>
      {description && <p className="text-text-secondary max-w-sm text-sm">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
