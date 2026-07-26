'use client';

import { getApiErrorMessage, type RaffleReportRow } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Card } from '@drawly/ui/Card';
import { DataTable, type Column } from '@drawly/ui/DataTable';
import { Loader } from '@drawly/ui/Loader';
import { PageHeader } from '@drawly/ui/PageHeader';
import { Pagination } from '@drawly/ui/Pagination';
import { ProgressBar } from '@drawly/ui/ProgressBar';
import { StatusBadge } from '@drawly/ui/StatusBadge';
import { formatCurrency } from '@drawly/utils';
import { useState } from 'react';

import { RAFFLE_STATUS_PRESENTATION } from '@/features/raffles';
import { api } from '@/lib/api';

import { useAnalyticsRaffles } from '../hooks/use-analytics';
import { formatChartDay } from '../services/format';
import {
  EMPTY_REPORT_FILTERS,
  toAnalyticsRafflesFilters,
  type ReportFilterValues,
} from '../validators/report-filters';
import { ExportButtons } from './export-buttons';
import { ReportFilters } from './report-filters';
import { ReportsNavTabs } from './reports-nav-tabs';

const PAGE_SIZE = 10;

const COLUMNS: Column<RaffleReportRow>[] = [
  {
    key: 'title',
    header: 'Rifa',
    render: (row) => (
      <div className="flex flex-col">
        <span className="text-text-primary font-medium">{row.title}</span>
        <span className="text-text-muted text-xs">Sorteo: {formatChartDay(row.draw_date)}</span>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Estado',
    render: (row) => (
      <StatusBadge
        label={RAFFLE_STATUS_PRESENTATION[row.status].label}
        tone={RAFFLE_STATUS_PRESENTATION[row.status].tone}
      />
    ),
  },
  { key: 'total', header: 'Boletas', render: (row) => row.total_tickets },
  { key: 'available', header: 'Disponibles', render: (row) => row.available },
  { key: 'reserved', header: 'Reservadas', render: (row) => row.reserved },
  { key: 'paid', header: 'Pagadas', render: (row) => row.paid },
  {
    key: 'percent',
    header: '% vendido',
    render: (row) => (
      <ProgressBar value={row.percent_sold} tone="success" size="sm" className="w-28" />
    ),
  },
  {
    key: 'expected',
    header: 'Ingresos esperados',
    render: (row) => <span className="font-medium">{formatCurrency(row.expected_revenue)}</span>,
  },
];

export function ReportsRaffles(): React.JSX.Element {
  const [filters, setFilters] = useState<ReportFilterValues>(EMPTY_REPORT_FILTERS);
  const [page, setPage] = useState(1);
  const query = toAnalyticsRafflesFilters(filters);
  const { data, isLoading, isError, error } = useAnalyticsRaffles(query, page, PAGE_SIZE);

  return (
    <>
      <PageHeader
        title="Reportes"
        description="Cantidad de boletas, porcentaje vendido e ingresos esperados por rifa."
        actions={
          <ExportButtons
            filenameBase="reporte-rifas"
            onExport={(format) => api.analytics.exportRaffles(format, query)}
          />
        }
      />

      <ReportsNavTabs />
      <ReportFilters
        fields={['dateRange', 'raffleStatus', 'collaborator']}
        value={filters}
        onChange={(next) => {
          setFilters(next);
          setPage(1);
        }}
      />

      {isLoading && <Loader label="Cargando rifas…" />}
      {isError && (
        <Alert tone="danger" title="No pudimos cargar el reporte">
          {getApiErrorMessage(error, 'Intenta de nuevo más tarde.')}
        </Alert>
      )}
      {data && (
        <div className="flex flex-col gap-3">
          <Card className="p-2 sm:p-4">
            <DataTable
              columns={COLUMNS}
              rows={data.data}
              getRowKey={(row) => row.id}
              empty={
                <p className="text-text-secondary py-6 text-sm">Sin rifas para este filtro.</p>
              }
            />
          </Card>
          {data.pagination.total_pages > 1 && (
            <Pagination
              page={page}
              pageCount={data.pagination.total_pages}
              onPageChange={setPage}
            />
          )}
        </div>
      )}
    </>
  );
}
