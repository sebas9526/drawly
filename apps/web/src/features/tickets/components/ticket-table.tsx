'use client';

import type { ParticipantDto, TicketDto } from '@drawly/api-client';
import { Button } from '@drawly/ui/Button';
import { DataTable, type Column, type DataTableSelection } from '@drawly/ui/DataTable';
import { EmptyState } from '@drawly/ui/EmptyState';
import { Select } from '@drawly/ui/Select';
import { StatusBadge } from '@drawly/ui/StatusBadge';
import { formatTicketNumber } from '@drawly/utils';
import { Ticket } from 'lucide-react';

import { TICKET_STATUS_PRESENTATION } from '../services/ticket-status';

interface TicketTableProps {
  tickets: TicketDto[];
  /** Largest generated ticket number (starting_number + total_tickets - 1) —
   * drives zero-padding width. */
  maxNumber: number;
  participants: ParticipantDto[];
  pendingTicketId: string | null;
  selection: DataTableSelection;
  emptyDescription?: string | undefined;
  onReserve: (ticketId: string) => void;
  onCancel: (ticketId: string) => void;
  onPay: (ticketId: string) => void;
  onAssignParticipant: (ticketId: string, participantId: string) => void;
  onRemoveParticipant: (ticketId: string) => void;
}

export function TicketTable({
  tickets,
  maxNumber,
  participants,
  pendingTicketId,
  selection,
  emptyDescription,
  onReserve,
  onCancel,
  onPay,
  onAssignParticipant,
  onRemoveParticipant,
}: TicketTableProps): React.JSX.Element {
  if (tickets.length === 0) {
    return (
      <EmptyState
        icon={<Ticket size={26} />}
        title="Sin boletas"
        description={
          emptyDescription ?? 'No hay boletas para este filtro. Genera boletas desde la rifa.'
        }
      />
    );
  }

  const columns: Column<TicketDto>[] = [
    {
      key: 'number',
      header: 'Número',
      render: (ticket) => (
        <span className="text-text-primary font-mono">
          {formatTicketNumber(ticket.number, maxNumber)}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Estado',
      render: (ticket) => {
        const presentation = TICKET_STATUS_PRESENTATION[ticket.status];
        return <StatusBadge label={presentation.label} tone={presentation.tone} />;
      },
    },
    {
      key: 'participant',
      header: 'Participante',
      render: (ticket) => {
        const isPending = pendingTicketId === ticket.id;
        const isLocked = ticket.status === 'paid' || ticket.status === 'winner';
        return (
          <Select
            className="max-w-[12rem]"
            value={ticket.participant_id ?? ''}
            disabled={isLocked || isPending}
            aria-label="Asignar participante"
            onChange={(event) => {
              const value = event.target.value;
              if (value === '') {
                if (ticket.participant_id) onRemoveParticipant(ticket.id);
              } else {
                onAssignParticipant(ticket.id, value);
              }
            }}
          >
            <option value="">— sin participante —</option>
            {participants.map((participant) => (
              <option key={participant.id} value={participant.id}>
                {participant.full_name}
              </option>
            ))}
          </Select>
        );
      },
    },
    {
      key: 'actions',
      header: 'Acciones',
      render: (ticket) => {
        const isPending = pendingTicketId === ticket.id;
        return (
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="outline"
              disabled={isPending || ticket.status !== 'available'}
              onClick={() => onReserve(ticket.id)}
            >
              Reservar
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={isPending || ticket.status !== 'reserved'}
              onClick={() => onCancel(ticket.id)}
            >
              Cancelar
            </Button>
            <Button
              size="sm"
              disabled={isPending || ticket.status !== 'reserved'}
              onClick={() => onPay(ticket.id)}
            >
              Pagar
            </Button>
          </div>
        );
      },
    },
  ];

  return (
    <DataTable
      columns={columns}
      rows={tickets}
      getRowKey={(ticket) => ticket.id}
      selection={selection}
      pageSize={20}
    />
  );
}
