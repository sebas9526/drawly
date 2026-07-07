import { Spinner } from './Spinner';

interface LoaderProps {
  label?: string;
}

export function Loader({ label = 'Cargando…' }: LoaderProps): React.JSX.Element {
  return (
    <div
      className="text-text-secondary flex items-center justify-center gap-2 py-10 text-sm"
      role="status"
    >
      <Spinner size={18} />
      {label}
    </div>
  );
}
