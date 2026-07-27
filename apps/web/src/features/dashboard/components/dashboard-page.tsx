'use client';

import {
  getApiErrorMessage,
  type DashboardRecentRaffle,
  type DashboardRecentReservation,
} from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { AnimatedNumber } from '@drawly/ui/AnimatedNumber';
import { DashboardCard } from '@drawly/ui/DashboardCard';
import { DataTable, type Column } from '@drawly/ui/DataTable';
import { LoadingCard } from '@drawly/ui/LoadingCard';
import { Modal } from '@drawly/ui/Modal';
import { PageHeader } from '@drawly/ui/PageHeader';
import { ProgressBar } from '@drawly/ui/ProgressBar';
import { StatCard } from '@drawly/ui/StatCard';
import { StatusBadge } from '@drawly/ui/StatusBadge';
import { useDisclosure } from '@drawly/ui/use-disclosure';
import { BadgeCheck, CalendarClock, Sparkles, Ticket, UserCog, Users } from 'lucide-react';
import { useMemo, useState } from 'react';

import { ROUTES } from '@drawly/constants';

import { RaffleForm, useRaffles } from '@/features/raffles';

import { useDashboardOverview } from '../hooks/use-dashboard';
import { formatCurrency, formatDateTime, RAFFLE_STATUS_PRESENTATION } from '../services/format';
import { QuickActions } from './quick-actions';
import { TicketDistributionChart } from './ticket-distribution-chart';

const RESERVATION_COLUMNS: Column<DashboardRecentReservation>[] = [
  { key: 'participant', header: 'Participante', render: (r) => r.participant_name ?? '—' },
  { key: 'raffle', header: 'Rifa', render: (r) => r.raffle_title },
  { key: 'number', header: 'Número', render: (r) => `#${r.number}` },
  { key: 'date', header: 'Fecha', render: (r) => formatDateTime(r.reserved_at) },
];

const RAFFLE_COLUMNS: Column<DashboardRecentRaffle>[] = [
  { key: 'title', header: 'Rifa', render: (r) => <span className="font-medium">{r.title}</span> },
  {
    key: 'status',
    header: 'Estado',
    render: (r) => (
      <StatusBadge
        label={RAFFLE_STATUS_PRESENTATION[r.status].label}
        tone={RAFFLE_STATUS_PRESENTATION[r.status].tone}
      />
    ),
  },
  { key: 'total', header: 'Boletas', render: (r) => r.total_tickets },
  { key: 'available', header: 'Disponibles', render: (r) => r.available_count },
];

export function DashboardPage(): React.JSX.Element {
  const { data, isLoading, isError, error } = useDashboardOverview();
  const { data: raffles } = useRaffles();
  const createRaffleModal = useDisclosure();
  const [createRafflePending, setCreateRafflePending] = useState(false);

  const publicRaffleHref = useMemo(() => {
    const published = raffles?.find((raffle) => raffle.status !== 'draft');
    return published ? ROUTES.PUBLIC_RAFFLE(published.public_slug) : null;
  }, [raffles]);

  const salesProgress = useMemo(() => {
    if (!data) return null;
    const total = data.tickets.total;
    if (total === 0) return { sold: 0, reserved: 0, available: 0 };
    return {
      sold: (data.tickets.paid / total) * 100,
      reserved: (data.tickets.reserved / total) * 100,
      available: (data.tickets.available / total) * 100,
    };
  }, [data]);

  return (
    <>
      <PageHeader title="Dashboard" description="Estado del negocio en tiempo real" />

      <QuickActions onCreateRaffle={createRaffleModal.open} publicRaffleHref={publicRaffleHref} />

      <Modal
        open={createRaffleModal.isOpen}
        onClose={createRaffleModal.close}
        closeDisabled={createRafflePending}
        title="Nueva rifa"
        className="max-w-xl"
      >
        <RaffleForm onDone={createRaffleModal.close} onPendingChange={setCreateRafflePending} />
      </Modal>

      {isLoading && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <LoadingCard key={index} lines={2} />
          ))}
        </div>
      )}

      {isError && (
        <Alert tone="danger" title="No pudimos cargar el dashboard">
          {getApiErrorMessage(error, 'Intenta de nuevo más tarde.')}
        </Alert>
      )}

      {data && (
        <>
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <StatCard
              href={ROUTES.RAFFLES}
              label="Mis rifas"
              value={<AnimatedNumber value={data.raffles.total} />}
              hint={`${data.raffles.active} activas`}
              icon={<Sparkles size={20} />}
              tone="primary"
            />
            <StatCard
              href={ROUTES.RAFFLES}
              label="Boletas"
              value={<AnimatedNumber value={data.tickets.total} />}
              icon={<Ticket size={20} />}
              tone="info"
            />
            <StatCard
              href={ROUTES.PARTICIPANTS}
              label="Participantes"
              value={<AnimatedNumber value={data.participants} />}
              icon={<Users size={20} />}
              tone="success"
            />
            <StatCard
              href={ROUTES.COLLABORATORS}
              label="Colaboradores"
              value={<AnimatedNumber value={data.collaborators} />}
              icon={<UserCog size={20} />}
              tone="primary"
            />
            <StatCard
              href="#recent-reservations"
              label="Reservas pendientes"
              value={<AnimatedNumber value={data.tickets.reserved} />}
              icon={<CalendarClock size={20} />}
              tone="warning"
            />
            <StatCard
              label="Boletas pagadas"
              value={<AnimatedNumber value={data.tickets.paid} />}
              icon={<BadgeCheck size={20} />}
              tone="success"
            />
          </section>

          {salesProgress && (
            <DashboardCard title="Progreso de ventas">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <ProgressBar label="Vendido" value={salesProgress.sold} tone="success" />
                <ProgressBar label="Reservado" value={salesProgress.reserved} tone="warning" />
                <ProgressBar label="Disponible" value={salesProgress.available} tone="info" />
              </div>
            </DashboardCard>
          )}

          <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <DashboardCard title="Distribución de boletas">
              <TicketDistributionChart
                available={data.tickets.available}
                reserved={data.tickets.reserved}
                paid={data.tickets.paid}
              />
            </DashboardCard>

            <DashboardCard title="Ventas (potencial)">
              <dl className="flex flex-col gap-3 text-sm">
                <div className="flex items-center justify-between">
                  <dt className="text-text-secondary">Valor potencial</dt>
                  <dd className="text-text-primary font-semibold">
                    {formatCurrency(data.sales.potential_value)}
                  </dd>
                </div>
                <div className="flex items-center justify-between">
                  <dt className="text-text-secondary">Valor reservado</dt>
                  <dd className="text-warning font-semibold">
                    {formatCurrency(data.sales.reserved_value)}
                  </dd>
                </div>
                <div className="flex items-center justify-between">
                  <dt className="text-text-secondary">Valor pagado</dt>
                  <dd className="text-success font-semibold">
                    {formatCurrency(data.sales.paid_value)}
                  </dd>
                </div>
              </dl>
            </DashboardCard>

            <DashboardCard title="Rifas por estado">
              <dl className="flex flex-col gap-3 text-sm">
                <div className="flex items-center justify-between">
                  <dt className="text-text-secondary">Borrador</dt>
                  <dd className="text-text-primary font-semibold">{data.raffles.draft}</dd>
                </div>
                <div className="flex items-center justify-between">
                  <dt className="text-text-secondary">Publicadas</dt>
                  <dd className="text-text-primary font-semibold">{data.raffles.published}</dd>
                </div>
                <div className="flex items-center justify-between">
                  <dt className="text-text-secondary">Finalizadas</dt>
                  <dd className="text-text-primary font-semibold">{data.raffles.closed}</dd>
                </div>
              </dl>
            </DashboardCard>
          </section>

          <div id="recent-reservations">
            <DashboardCard title="Últimas reservas">
              <DataTable
                columns={RESERVATION_COLUMNS}
                rows={data.recent_reservations}
                getRowKey={(_, index) => `reservation-${index}`}
                empty={<p className="text-text-secondary py-4 text-sm">Aún no hay reservas.</p>}
              />
            </DashboardCard>
          </div>

          <DashboardCard title="Rifas recientes">
            <DataTable
              columns={RAFFLE_COLUMNS}
              rows={data.recent_raffles}
              getRowKey={(_, index) => `raffle-${index}`}
              empty={<p className="text-text-secondary py-4 text-sm">Aún no hay rifas.</p>}
            />
          </DashboardCard>
        </>
      )}
    </>
  );
}
