'use client';

import { isApiError, type PublicReserveResult } from '@drawly/api-client';
import { Card } from '@drawly/ui/Card';
import { EmptyState } from '@drawly/ui/EmptyState';
import { Skeleton } from '@drawly/ui/Skeleton';
import { ThemeToggle } from '@drawly/ui/ThemeToggle';
import { Ticket } from 'lucide-react';
import { useSearchParams } from 'next/navigation';
import { useMemo, useState } from 'react';

import {
  usePublicCollaborators,
  usePublicRaffle,
  usePublicReserve,
  usePublicTickets,
} from '../hooks/use-public-raffle';
import type { PublicTicketFilter } from '../services/ticket-status';
import { reserveFormSchema, type ReserveFormValues } from '../validators/reserve-form';
import { Confirmation } from './confirmation';
import { RaffleHeader } from './raffle-header';
import { ReserveForm } from './reserve-form';
import { TicketGrid } from './ticket-grid';

function Shell({ children }: { children: React.ReactNode }): React.JSX.Element {
  return (
    <div className="bg-background text-text-primary min-h-screen">
      <header className="border-border bg-surface/80 sticky top-0 z-20 border-b backdrop-blur">
        <div className="mx-auto flex h-14 w-full max-w-3xl items-center justify-between px-6">
          <span className="text-text-primary flex items-center gap-2 font-semibold">
            <span className="bg-primary text-primary-fg flex h-7 w-7 items-center justify-center rounded-lg">
              <Ticket size={16} />
            </span>
            Drawly
          </span>
          <ThemeToggle />
        </div>
      </header>
      <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">{children}</main>
    </div>
  );
}

export function PublicRafflePage({ slug }: { slug: string }): React.JSX.Element {
  const raffleQuery = usePublicRaffle(slug);
  const ticketsQuery = usePublicTickets(slug);
  const collaboratorsQuery = usePublicCollaborators(slug);
  const reserve = usePublicReserve(slug);
  const refParam = useSearchParams().get('ref');

  const lockedCollaborator = useMemo(
    () => collaboratorsQuery.data?.find((collaborator) => collaborator.id === refParam) ?? null,
    [collaboratorsQuery.data, refParam],
  );

  const [filter, setFilter] = useState<PublicTicketFilter>('all');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<number | null>(null);
  const [confirmation, setConfirmation] = useState<PublicReserveResult | null>(null);

  if (raffleQuery.isLoading) {
    return (
      <Shell>
        <Skeleton className="h-52 w-full" />
        <Skeleton className="h-6 w-1/2" />
        <Skeleton className="h-40 w-full" />
      </Shell>
    );
  }

  if (raffleQuery.isError || !raffleQuery.data) {
    return (
      <Shell>
        <EmptyState
          icon={<Ticket size={28} />}
          title="Rifa no disponible"
          description={
            isApiError(raffleQuery.error)
              ? 'Esta rifa no existe o aún no está publicada.'
              : 'No pudimos cargar la rifa. Intenta de nuevo más tarde.'
          }
        />
      </Shell>
    );
  }

  const raffle = raffleQuery.data;
  const maxNumber = raffle.starting_number + raffle.total_tickets - 1;

  if (confirmation) {
    return (
      <Shell>
        <Confirmation
          result={confirmation}
          onReserveAnother={() => {
            setConfirmation(null);
            setSelected(null);
          }}
        />
      </Shell>
    );
  }

  const handleSubmit = (values: ReserveFormValues): void => {
    if (selected === null || !reserveFormSchema.safeParse(values).success) return;
    reserve.mutate(
      {
        ticket_number: selected,
        participant: {
          full_name: values.full_name.trim(),
          phone: values.phone.trim(),
          email: values.email.trim() || undefined,
          document: values.document.trim() || undefined,
        },
        collaborator_id: values.collaborator_id || undefined,
      },
      { onSuccess: (result) => setConfirmation(result) },
    );
  };

  const reserveErrorMessage = reserve.isError
    ? isApiError(reserve.error)
      ? reserve.error.message
      : 'No se pudo reservar. Intenta con otra boleta.'
    : null;

  return (
    <Shell>
      <RaffleHeader raffle={raffle} />
      <Card className="p-5">
        {selected === null ? (
          <TicketGrid
            tickets={ticketsQuery.data ?? []}
            maxNumber={maxNumber}
            loading={ticketsQuery.isLoading}
            filter={filter}
            search={search}
            onFilter={setFilter}
            onSearch={setSearch}
            onSelect={(ticketNumber) => {
              reserve.reset();
              setSelected(ticketNumber);
            }}
          />
        ) : (
          <ReserveForm
            ticketNumber={selected}
            maxNumber={maxNumber}
            pending={reserve.isPending}
            errorMessage={reserveErrorMessage}
            collaborators={collaboratorsQuery.data ?? []}
            lockedCollaborator={lockedCollaborator}
            onSubmit={handleSubmit}
            onCancel={() => {
              reserve.reset();
              setSelected(null);
            }}
          />
        )}
      </Card>
    </Shell>
  );
}
