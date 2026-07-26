'use client';

import { getApiErrorMessage, type CollaboratorStatsDto } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { DashboardCard } from '@drawly/ui/DashboardCard';
import { DataTable, type Column } from '@drawly/ui/DataTable';
import { EmptyState } from '@drawly/ui/EmptyState';
import { Loader } from '@drawly/ui/Loader';
import { formatCurrency } from '@drawly/utils';
import { UserCog } from 'lucide-react';

import { useCollaboratorStats } from '../hooks/use-collaborators';

const COLUMNS: Column<CollaboratorStatsDto>[] = [
  {
    key: 'name',
    header: 'Colaborador',
    render: (s) => (
      <span className="flex items-center gap-2 font-medium">
        <span
          className="inline-block h-3 w-3 shrink-0 rounded-full"
          style={{ backgroundColor: s.color }}
          aria-hidden
        />
        {s.name}
      </span>
    ),
  },
  { key: 'reserved', header: 'Reservadas', render: (s) => s.total },
  { key: 'paid', header: 'Pagadas', render: (s) => s.paid },
  { key: 'pending', header: 'Pendientes', render: (s) => s.reserved },
  {
    key: 'value',
    header: 'Total vendido',
    render: (s) => <span className="font-medium">{formatCurrency(s.total_value)}</span>,
  },
];

export function CollaboratorStats({ raffleId }: { raffleId: string }): React.JSX.Element {
  const { data, isLoading, isError, error } = useCollaboratorStats(raffleId);

  const count = data?.length ?? 0;

  return (
    <DashboardCard
      title="Ventas por colaborador"
      action={
        <span className="text-text-secondary text-sm">
          {count} {count === 1 ? 'colaborador' : 'colaboradores'}
        </span>
      }
    >
      {isLoading && <Loader label="Cargando estadísticas…" />}
      {isError && (
        <Alert tone="danger">
          {getApiErrorMessage(error, 'No se pudieron cargar las estadísticas.')}
        </Alert>
      )}
      {data && data.length === 0 && (
        <EmptyState
          icon={<UserCog size={26} />}
          title="Sin colaboradores"
          description="Añade colaboradores a esta rifa para ver sus ventas."
        />
      )}
      {data && data.length > 0 && (
        <DataTable columns={COLUMNS} rows={data} getRowKey={(s) => s.collaborator_id} />
      )}
    </DashboardCard>
  );
}
