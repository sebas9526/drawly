'use client';

import { getApiErrorMessage } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { DashboardCard } from '@drawly/ui/DashboardCard';
import { Loader } from '@drawly/ui/Loader';
import { SearchInput } from '@drawly/ui/SearchInput';
import { StatCard } from '@drawly/ui/StatCard';
import { formatCurrency } from '@drawly/utils';
import { BadgeCheck, CalendarClock, CircleDollarSign, Ticket } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import { useRaffleCollaborators } from '@/features/collaborators';
import { useParticipants } from '@/features/participants';

import { useBulkTicketActions, useTicketActions } from '../hooks/use-ticket-actions';
import { useTickets } from '../hooks/use-tickets';
import type { TicketStatusFilter } from '../validators/ticket-filters';
import { BulkActionBar } from './bulk-action-bar';
import { TicketStatusFilterControl } from './ticket-status-filter';
import { TicketTable } from './ticket-table';

interface TicketsAdminProps {
  raffleId: string;
  /** Raffle's configured ticket count. */
  total: number;
  /** First generated ticket number (0 or 1) — combined with `total` to derive
   * the zero-padding width. */
  startingNumber: number;
  ticketPrice: number;
  /** Whether the raffle is currently published — the backend rejects
   * reserve/pay/assign-participant while it isn't (still draft, including
   * one waiting on a scheduled activation date). */
  raffleIsOpen: boolean;
}

export function TicketsAdmin({
  raffleId,
  total,
  startingNumber,
  ticketPrice,
  raffleIsOpen,
}: TicketsAdminProps): React.JSX.Element {
  const [filter, setFilter] = useState<TicketStatusFilter>('all');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [bulkNotice, setBulkNotice] = useState<string | null>(null);

  const { data, isLoading, isError, error } = useTickets(raffleId);
  const { data: participants } = useParticipants();
  const { data: collaborators } = useRaffleCollaborators(raffleId);
  const { reserve, cancel, pay, assignParticipant, unassignParticipant } = useTicketActions();
  const bulk = useBulkTicketActions();

  useEffect(() => {
    if (!bulkNotice) return;
    const timeout = setTimeout(() => setBulkNotice(null), 5000);
    return () => clearTimeout(timeout);
  }, [bulkNotice]);

  const allTickets = useMemo(() => data ?? [], [data]);

  const counts = useMemo(
    () => ({
      all: allTickets.length,
      available: allTickets.filter((t) => t.status === 'available').length,
      reserved: allTickets.filter((t) => t.status === 'reserved').length,
      paid: allTickets.filter((t) => t.status === 'paid').length,
    }),
    [allTickets],
  );

  const filteredTickets = useMemo(() => {
    const query = search.trim().toLowerCase();
    return allTickets.filter((ticket) => {
      if (filter !== 'all' && ticket.status !== filter) return false;
      if (!query) return true;
      const participant = participants?.find((p) => p.id === ticket.participant_id);
      return (
        String(ticket.number).includes(query) ||
        (participant?.full_name.toLowerCase().includes(query) ?? false)
      );
    });
  }, [allTickets, filter, search, participants]);

  const pendingTicketId = useMemo(() => {
    return (
      reserve.variables ??
      cancel.variables ??
      pay.variables ??
      unassignParticipant.variables ??
      assignParticipant.variables?.ticketId ??
      null
    );
  }, [
    reserve.variables,
    cancel.variables,
    pay.variables,
    unassignParticipant.variables,
    assignParticipant.variables,
  ]);

  const actionError =
    reserve.error ??
    cancel.error ??
    pay.error ??
    assignParticipant.error ??
    unassignParticipant.error;

  const toggleSelection = (id: string): void => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleSelectionAll = (ids: string[]): void => {
    setSelected((prev) => {
      const allSelected = ids.every((id) => prev.has(id));
      const next = new Set(prev);
      if (allSelected) ids.forEach((id) => next.delete(id));
      else ids.forEach((id) => next.add(id));
      return next;
    });
  };

  const runBulk = async (
    label: string,
    action: (ids: string[]) => Promise<{ succeeded: number; failed: number }>,
  ): Promise<void> => {
    const ids = Array.from(selected);
    const result = await action(ids);
    setSelected(new Set());
    setBulkNotice(
      result.failed === 0
        ? `${label}: ${result.succeeded} boletas actualizadas.`
        : `${label}: ${result.succeeded} actualizadas, ${result.failed} no aplicaban.`,
    );
  };

  return (
    <div className="flex flex-col gap-4">
      <section className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard
          label="Disponibles"
          value={counts.available}
          icon={<Ticket size={20} />}
          tone="success"
        />
        <StatCard
          label="Reservadas"
          value={counts.reserved}
          icon={<CalendarClock size={20} />}
          tone="warning"
        />
        <StatCard label="Pagadas" value={counts.paid} icon={<BadgeCheck size={20} />} tone="info" />
        <StatCard
          label="Ingresos potenciales"
          value={formatCurrency(total * ticketPrice)}
          icon={<CircleDollarSign size={20} />}
          tone="primary"
        />
      </section>

      <DashboardCard
        title="Boletas"
        action={<TicketStatusFilterControl value={filter} onChange={setFilter} counts={counts} />}
      >
        <div className="flex flex-col gap-4">
          <SearchInput
            containerClassName="max-w-sm"
            placeholder="Buscar por número o participante"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          {!raffleIsOpen && (
            <Alert tone="info">
              Esta rifa aún no está publicada: no se pueden reservar ni pagar boletas hasta que se
              publique.
            </Alert>
          )}

          {selected.size > 0 && (
            <BulkActionBar
              selectedCount={selected.size}
              collaborators={collaborators ?? []}
              isPending={bulk.isPending}
              raffleIsOpen={raffleIsOpen}
              onReserve={() => void runBulk('Reservar', bulk.bulkReserve)}
              onCancel={() => void runBulk('Cancelar', bulk.bulkCancel)}
              onMarkPaid={() => void runBulk('Marcar pagadas', bulk.bulkMarkPaid)}
              onSetCollaborator={(collaboratorId) =>
                void runBulk('Cambiar colaborador', (ids) =>
                  bulk.bulkSetCollaborator(ids, collaboratorId),
                )
              }
              onClearSelection={() => setSelected(new Set())}
            />
          )}

          {bulkNotice && <Alert tone="info">{bulkNotice}</Alert>}

          {actionError && (
            <Alert tone="danger">{getApiErrorMessage(actionError, 'La acción falló.')}</Alert>
          )}
          {isLoading && <Loader label="Cargando boletas…" />}
          {isError && (
            <Alert tone="danger">
              {getApiErrorMessage(error, 'No se pudieron cargar las boletas.')}
            </Alert>
          )}
          {data && (
            <TicketTable
              tickets={filteredTickets}
              maxNumber={startingNumber + total - 1}
              participants={participants ?? []}
              pendingTicketId={pendingTicketId}
              raffleIsOpen={raffleIsOpen}
              emptyDescription={
                search || filter !== 'all'
                  ? 'No hay boletas que coincidan con tu búsqueda o filtro.'
                  : undefined
              }
              selection={{
                selectedKeys: selected,
                onToggle: toggleSelection,
                onToggleAll: toggleSelectionAll,
              }}
              onReserve={(id) => reserve.mutate(id)}
              onCancel={(id) => cancel.mutate(id)}
              onPay={(id) => pay.mutate(id)}
              onAssignParticipant={(ticketId, participantId) =>
                assignParticipant.mutate({ ticketId, participantId })
              }
              onRemoveParticipant={(ticketId) => unassignParticipant.mutate(ticketId)}
            />
          )}
        </div>
      </DashboardCard>
    </div>
  );
}
