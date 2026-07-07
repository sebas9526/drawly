'use client';

import { isApiError, type CollaboratorReportRow } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Card } from '@drawly/ui/Card';
import { DataTable, type Column } from '@drawly/ui/DataTable';
import { EmptyState } from '@drawly/ui/EmptyState';
import { Loader } from '@drawly/ui/Loader';
import { PageHeader } from '@drawly/ui/PageHeader';
import { ProgressBar } from '@drawly/ui/ProgressBar';
import { formatCurrency } from '@drawly/utils';
import { UserCog } from 'lucide-react';
import { useState } from 'react';

import { api } from '@/lib/api';

import { useAnalyticsCollaborators } from '../hooks/use-analytics';
import {
  EMPTY_REPORT_FILTERS,
  toAnalyticsFilters,
  type ReportFilterValues,
} from '../validators/report-filters';
import { ExportButtons } from './export-buttons';
import { ReportFilters } from './report-filters';
import { ReportsNavTabs } from './reports-nav-tabs';

const COLUMNS: Column<CollaboratorReportRow>[] = [
  {
    key: 'rank',
    header: '#',
    render: (row) => (
      <span className="bg-muted text-text-secondary inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold">
        {row.rank}
      </span>
    ),
  },
  {
    key: 'name',
    header: 'Colaborador',
    render: (row) => <span className="font-medium">{row.name}</span>,
  },
  { key: 'raffle', header: 'Rifa', render: (row) => row.raffle_title },
  { key: 'sales', header: 'Ventas', render: (row) => row.total_sales },
  { key: 'reservations', header: 'Reservas', render: (row) => row.total_reservations },
  { key: 'served', header: 'Participantes atendidos', render: (row) => row.participants_served },
  {
    key: 'amount',
    header: 'Monto esperado',
    render: (row) => <span className="font-medium">{formatCurrency(row.expected_amount)}</span>,
  },
  {
    key: 'participation',
    header: '% participación',
    render: (row) => (
      <ProgressBar value={row.participation_percent} tone="info" size="sm" className="w-28" />
    ),
  },
];

export function ReportsCollaborators(): React.JSX.Element {
  const [filters, setFilters] = useState<ReportFilterValues>(EMPTY_REPORT_FILTERS);
  const query = toAnalyticsFilters(filters);
  const { data, isLoading, isError, error } = useAnalyticsCollaborators(query);

  return (
    <>
      <PageHeader
        title="Reportes"
        description="Ranking de colaboradores por monto esperado."
        actions={
          <ExportButtons
            filenameBase="reporte-colaboradores"
            onExport={(format) => api.analytics.exportCollaborators(format, query)}
          />
        }
      />

      <ReportsNavTabs />
      <ReportFilters fields={['dateRange', 'raffle']} value={filters} onChange={setFilters} />

      {isLoading && <Loader label="Cargando colaboradores…" />}
      {isError && (
        <Alert tone="danger" title="No pudimos cargar el reporte">
          {isApiError(error) ? error.message : 'Intenta de nuevo más tarde.'}
        </Alert>
      )}
      {data && data.length === 0 && (
        <EmptyState
          icon={<UserCog size={28} />}
          title="Sin colaboradores"
          description="No hay ventas de colaboradores para este filtro."
        />
      )}
      {data && data.length > 0 && (
        <Card className="p-2 sm:p-4">
          <DataTable columns={COLUMNS} rows={data} getRowKey={(row) => row.id} pageSize={10} />
        </Card>
      )}
    </>
  );
}
