import { Label } from './Label';

interface FieldProps {
  label?: string;
  hint?: string;
  error?: string | undefined;
  htmlFor?: string;
  children: React.ReactNode;
}

export function Field({ label, hint, error, htmlFor, children }: FieldProps): React.JSX.Element {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <Label htmlFor={htmlFor}>{label}</Label>}
      {children}
      {error ? (
        <p className="text-danger text-xs">{error}</p>
      ) : hint ? (
        <p className="text-text-muted text-xs">{hint}</p>
      ) : null}
    </div>
  );
}
