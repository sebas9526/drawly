'use client';

import { getApiErrorMessage, type ParticipantReportRow } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Card } from '@drawly/ui/Card';
import { DataTable, type Column } from '@drawly/ui/DataTable';
import { EmptyState } from '@drawly/ui/EmptyState';
import { Loader } from '@drawly/ui/Loader';
import { PageHeader } from '@drawly/ui/PageHeader';
import { formatCurrency } from '@drawly/utils';
import { Users } from 'lucide-react';
import { useState } from 'react';

import { api } from '@/lib/api';

import { useAnalyticsParticipants } from '../hooks/use-analytics';
import { formatChartDay } from '../services/format';
import {
  EMPTY_REPORT_FILTERS,
  toAnalyticsFilters,
  type ReportFilterValues,
} from '../validators/report-filters';
import { ExportButtons } from './export-buttons';
import { ReportFilters } from './report-filters';
import { ReportsNavTabs } from './reports-nav-tabs';

const COLUMNS: Column<ParticipantReportRow>[] = [
  {
    key: 'name',
    header: 'Participante',
    sortable: true,
    sortValue: (row) => row.full_name,
    render: (row) => <span className="font-medium">{row.full_name}</span>,
  },
  {
    key: 'purchases',
    header: 'Compras',
    sortable: true,
    sortValue: (row) => row.purchases_count,
    render: (row) => row.purchases_count,
  },
  {
    key: 'tickets',
    header: 'Boletas',
    sortable: true,
    sortValue: (row) => row.tickets_count,
    render: (row) => row.tickets_count,
  },
  {
    key: 'invested',
    header: 'Valor invertido',
    sortable: true,
    sortValue: (row) => row.amount_invested,
    render: (row) => <span className="font-medium">{formatCurrency(row.amount_invested)}</span>,
  },
  {
    key: 'last_purchase',
    header: 'Última compra',
    render: (row) => (row.last_purchase_at ? formatChartDay(row.last_purchase_at) : '—'),
  },
  { key: 'raffles', header: 'Rifas', render: (row) => row.raffles_count },
];

export function ReportsParticipants(): React.JSX.Element {
  const [filters, setFilters] = useState<ReportFilterValues>(EMPTY_REPORT_FILTERS);
  const query = toAnalyticsFilters(filters);
  const { data, isLoading, isError, error } = useAnalyticsParticipants(query);

  return (
    <>
      <PageHeader
        title="Reportes"
        description="Compras, boletas y valor invertido por participante."
        actions={
          <ExportButtons
            filenameBase="reporte-participantes"
            onExport={(format) => api.analytics.exportParticipants(format, query)}
          />
        }
      />

      <ReportsNavTabs />
      <ReportFilters
        fields={['dateRange', 'raffle', 'collaborator', 'status']}
        value={filters}
        onChange={setFilters}
      />

      {isLoading && <Loader label="Cargando participantes…" />}
      {isError && (
        <Alert tone="danger" title="No pudimos cargar el reporte">
          {getApiErrorMessage(error, 'Intenta de nuevo más tarde.')}
        </Alert>
      )}
      {data && data.length === 0 && (
        <EmptyState
          icon={<Users size={28} />}
          title="Sin participantes"
          description="No hay compras de participantes para este filtro."
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
