'use client';

import { getApiErrorMessage } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Card } from '@drawly/ui/Card';
import { DashboardCard } from '@drawly/ui/DashboardCard';
import { EmptyState } from '@drawly/ui/EmptyState';
import { Loader } from '@drawly/ui/Loader';
import { ProgressBar } from '@drawly/ui/ProgressBar';
import { StatCard } from '@drawly/ui/StatCard';
import { formatCurrency } from '@drawly/utils';
import { Award, CircleDollarSign, ShoppingBag, Ticket } from 'lucide-react';
import { useMemo } from 'react';

import { useCollaboratorStats } from '../hooks/use-collaborators';

interface CollaboratorLeaderboardProps {
  raffleId: string;
  raffleTotalTickets: number;
}

/** Sales ranking for a single raffle's collaborators. Stats are per-raffle
 * (see CollaboratorStatsDto), so this only renders once a raffle is selected. */
export function CollaboratorLeaderboard({
  raffleId,
  raffleTotalTickets,
}: CollaboratorLeaderboardProps): React.JSX.Element {
  const { data, isLoading, isError, error } = useCollaboratorStats(raffleId);

  const ranked = useMemo(
    () => [...(data ?? [])].sort((a, b) => b.total_value - a.total_value),
    [data],
  );

  const totals = useMemo(
    () =>
      (data ?? []).reduce(
        (acc, stat) => ({
          paid: acc.paid + stat.paid,
          reserved: acc.reserved + stat.reserved,
          value: acc.value + stat.total_value,
        }),
        { paid: 0, reserved: 0, value: 0 },
      ),
    [data],
  );

  if (isLoading) return <Loader label="Cargando ranking…" />;

  if (isError) {
    return (
      <Alert tone="danger">
        {getApiErrorMessage(error, 'No se pudo cargar el ranking de colaboradores.')}
      </Alert>
    );
  }

  if (!data || data.length === 0) {
    return (
      <EmptyState
        icon={<Award size={26} />}
        title="Sin colaboradores"
        description="Añade colaboradores a esta rifa para ver su ranking de ventas."
      />
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          label="Total vendido"
          value={totals.paid}
          icon={<ShoppingBag size={20} />}
          tone="success"
        />
        <StatCard
          label="Total reservado"
          value={totals.reserved}
          icon={<Ticket size={20} />}
          tone="warning"
        />
        <StatCard
          label="Dinero recaudado"
          value={formatCurrency(totals.value)}
          icon={<CircleDollarSign size={20} />}
          tone="primary"
        />
      </section>

      <DashboardCard title="Ranking de colaboradores">
        <div className="flex flex-col gap-3">
          {ranked.map((stat, index) => {
            const soldPct = raffleTotalTickets > 0 ? (stat.paid / raffleTotalTickets) * 100 : 0;
            return (
              <Card key={stat.collaborator_id} className="flex flex-col gap-2 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div className="flex min-w-0 items-center gap-3">
                    <span className="bg-muted text-text-secondary flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold">
                      #{index + 1}
                    </span>
                    <span
                      className="inline-block h-3 w-3 shrink-0 rounded-full"
                      style={{ backgroundColor: stat.color }}
                      aria-hidden
                    />
                    <span className="text-text-primary truncate font-medium">{stat.name}</span>
                  </div>
                  <span className="text-text-primary shrink-0 text-sm font-semibold">
                    {formatCurrency(stat.total_value)}
                  </span>
                </div>
                <ProgressBar
                  value={soldPct}
                  tone="success"
                  label={`${stat.paid} pagadas de ${raffleTotalTickets}`}
                />
              </Card>
            );
          })}
        </div>
      </DashboardCard>
    </div>
  );
}
