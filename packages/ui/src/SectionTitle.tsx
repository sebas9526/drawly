interface SectionTitleProps {
  children: React.ReactNode;
  action?: React.ReactNode;
}

export function SectionTitle({ children, action }: SectionTitleProps): React.JSX.Element {
  return (
    <div className="mb-3 flex items-center justify-between">
      <h2 className="text-text-primary text-base font-semibold">{children}</h2>
      {action}
    </div>
  );
}
