'use client';

import { PageHeader } from '@drawly/ui/PageHeader';
import { useParams } from 'next/navigation';

import { ROUTES } from '@drawly/constants';

import { AppShell } from '@/components/shell/app-shell';
import { CollaboratorStats } from '@/features/collaborators';
import { useRaffle } from '@/features/raffles';
import { TicketsAdmin } from '@/features/tickets';

export default function RaffleTicketsPage(): React.JSX.Element {
  const params = useParams<{ raffleId: string }>();
  const raffleId = params.raffleId;
  const { data: raffle, isLoading } = useRaffle(raffleId);

  return (
    <AppShell
      breadcrumbs={[
        { label: 'Rifas', href: ROUTES.RAFFLES },
        { label: raffle?.title ?? 'Boletas' },
      ]}
    >
      <PageHeader
        title={raffle?.title ?? 'Boletas'}
        description="Administra las boletas de esta rifa."
      />
      {isLoading && <p className="text-text-secondary text-sm">Cargando rifa…</p>}
      {raffle && (
        <>
          <TicketsAdmin
            raffleId={raffleId}
            total={raffle.total_tickets}
            startingNumber={raffle.starting_number}
            ticketPrice={raffle.ticket_price}
            raffleIsOpen={raffle.status === 'published'}
          />
          <CollaboratorStats raffleId={raffleId} />
        </>
      )}
    </AppShell>
  );
}
