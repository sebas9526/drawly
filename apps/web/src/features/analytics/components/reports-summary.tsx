'use client';

import { isApiError } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { AnimatedNumber } from '@drawly/ui/AnimatedNumber';
import { BarChart } from '@drawly/ui/BarChart';
import { DashboardCard } from '@drawly/ui/DashboardCard';
import { DonutChart } from '@drawly/ui/DonutChart';
import { LoadingCard } from '@drawly/ui/LoadingCard';
import { PageHeader } from '@drawly/ui/PageHeader';
import { ProgressBar } from '@drawly/ui/ProgressBar';
import { StatCard } from '@drawly/ui/StatCard';
import { TONE_CHART_COLOR } from '@drawly/ui/tones';
import { formatCurrency } from '@drawly/utils';
import {
  BadgeCheck,
  CalendarClock,
  CircleDollarSign,
  Sparkles,
  Ticket,
  UserCog,
  Users,
  Wallet,
} from 'lucide-react';
import { useState } from 'react';

import { api } from '@/lib/api';

import { useAnalyticsDashboard, useAnalyticsSales } from '../hooks/use-analytics';
import { formatChartDay } from '../services/format';
import {
  EMPTY_REPORT_FILTERS,
  toAnalyticsFilters,
  type ReportFilterValues,
} from '../validators/report-filters';
import { ExportButtons } from './export-buttons';
import { ReportFilters } from './report-filters';
import { ReportsNavTabs } from './reports-nav-tabs';

export function ReportsSummary(): React.JSX.Element {
  const [filters, setFilters] = useState<ReportFilterValues>(EMPTY_REPORT_FILTERS);
  const query = toAnalyticsFilters(filters);

  const dashboard = useAnalyticsDashboard(query);
  const sales = useAnalyticsSales(query);

  return (
    <>
      <PageHeader
        title="Reportes"
        description="Analítica del negocio: rifas, boletas, colaboradores y participantes."
        actions={
          <ExportButtons
            filenameBase="dashboard"
            onExport={(format) => api.analytics.exportDashboard(format, query)}
          />
        }
      />

      <ReportsNavTabs />
      <ReportFilters
        fields={['dateRange', 'raffle', 'collaborator', 'status']}
        value={filters}
        onChange={setFilters}
      />

      {dashboard.isLoading && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <LoadingCard key={index} lines={2} />
          ))}
        </div>
      )}
      {dashboard.isError && (
        <Alert tone="danger" title="No pudimos cargar el resumen">
          {isApiError(dashboard.error) ? dashboard.error.message : 'Intenta de nuevo más tarde.'}
        </Alert>
      )}

      {dashboard.data && (
        <>
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label="Rifas"
              value={<AnimatedNumber value={dashboard.data.raffles_total} />}
              hint={`${dashboard.data.raffles_published} publicadas`}
              icon={<Sparkles size={20} />}
              tone="primary"
            />
            <StatCard
              label="Disponibles"
              value={<AnimatedNumber value={dashboard.data.tickets_available} />}
              icon={<Ticket size={20} />}
              tone="success"
            />
            <StatCard
              label="Reservadas"
              value={<AnimatedNumber value={dashboard.data.tickets_reserved} />}
              icon={<CalendarClock size={20} />}
              tone="warning"
            />
            <StatCard
              label="Pagadas"
              value={<AnimatedNumber value={dashboard.data.tickets_paid} />}
              icon={<BadgeCheck size={20} />}
              tone="info"
            />
            <StatCard
              label="Participantes"
              value={<AnimatedNumber value={dashboard.data.participants_total} />}
              icon={<Users size={20} />}
              tone="primary"
            />
            <StatCard
              label="Colaboradores"
              value={<AnimatedNumber value={dashboard.data.collaborators_total} />}
              icon={<UserCog size={20} />}
              tone="primary"
            />
            <StatCard
              label="Ingresos esperados"
              value={formatCurrency(dashboard.data.expected_revenue)}
              icon={<CircleDollarSign size={20} />}
              tone="info"
            />
            <StatCard
              label="Ingresos recibidos"
              value={formatCurrency(dashboard.data.received_revenue)}
              icon={<Wallet size={20} />}
              tone="success"
            />
          </section>

          <DashboardCard title="Progreso">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <ProgressBar label="Vendido" value={dashboard.data.percent_sold} tone="success" />
              <ProgressBar
                label="Reservado"
                value={dashboard.data.percent_reserved}
                tone="warning"
              />
            </div>
          </DashboardCard>
        </>
      )}

      {sales.isError && (
        <Alert tone="danger" title="No pudimos cargar las gráficas">
          {isApiError(sales.error) ? sales.error.message : 'Intenta de nuevo más tarde.'}
        </Alert>
      )}

      {sales.data && (
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <DashboardCard title="Estado de boletas">
            <DonutChart
              ariaLabel="Estado de boletas"
              emptyTitle="Sin boletas"
              segments={[
                {
                  key: 'available',
                  label: 'Disponibles',
                  value: sales.data.status_distribution.available,
                  color: TONE_CHART_COLOR.success,
                },
                {
                  key: 'reserved',
                  label: 'Reservadas',
                  value: sales.data.status_distribution.reserved,
                  color: TONE_CHART_COLOR.warning,
                },
                {
                  key: 'paid',
                  label: 'Pagadas',
                  value: sales.data.status_distribution.paid,
                  color: TONE_CHART_COLOR.info,
                },
                {
                  key: 'cancelled',
                  label: 'Canceladas',
                  value: sales.data.status_distribution.cancelled,
                  color: TONE_CHART_COLOR.neutral,
                },
                {
                  key: 'winner',
                  label: 'Ganadoras',
                  value: sales.data.status_distribution.winner,
                  color: TONE_CHART_COLOR.primary,
                },
              ]}
            />
          </DashboardCard>

          <DashboardCard title="Ventas por día">
            <BarChart
              emptyTitle="Sin ventas en el rango seleccionado"
              data={sales.data.sales_by_day.map((point) => ({
                label: formatChartDay(point.day),
                value: point.count,
              }))}
            />
          </DashboardCard>

          <DashboardCard title="Reservas por día">
            <BarChart
              emptyTitle="Sin reservas en el rango seleccionado"
              data={sales.data.reservations_by_day.map((point) => ({
                label: formatChartDay(point.day),
                value: point.count,
              }))}
            />
          </DashboardCard>

          <DashboardCard title="Top colaboradores">
            <BarChart
              orientation="horizontal"
              emptyTitle="Sin ventas de colaboradores todavía"
              formatValue={formatCurrency}
              data={sales.data.top_collaborators.map((row) => ({
                label: row.name,
                value: row.value,
              }))}
            />
          </DashboardCard>

          <DashboardCard title="Top rifas">
            <BarChart
              orientation="horizontal"
              emptyTitle="Sin ventas todavía"
              formatValue={formatCurrency}
              data={sales.data.top_raffles.map((row) => ({ label: row.name, value: row.value }))}
            />
          </DashboardCard>

          <DashboardCard title="Top participantes">
            <BarChart
              orientation="horizontal"
              emptyTitle="Sin compras todavía"
              formatValue={formatCurrency}
              data={sales.data.top_participants.map((row) => ({
                label: row.name,
                value: row.value,
              }))}
            />
          </DashboardCard>
        </section>
      )}
    </>
  );
}
