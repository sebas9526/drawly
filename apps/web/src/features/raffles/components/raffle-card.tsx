'use client';

import { getApiErrorMessage, type RaffleDto } from '@drawly/api-client';
import { ActionMenu } from '@drawly/ui/ActionMenu';
import { Alert } from '@drawly/ui/Alert';
import { Button } from '@drawly/ui/Button';
import { Card } from '@drawly/ui/Card';
import { Field } from '@drawly/ui/Field';
import { Input } from '@drawly/ui/Input';
import { Modal } from '@drawly/ui/Modal';
import { ProgressBar } from '@drawly/ui/ProgressBar';
import { StatusBadge } from '@drawly/ui/StatusBadge';
import { useDisclosure } from '@drawly/ui/use-disclosure';
import {
  Calendar,
  Clock,
  Copy,
  ExternalLink,
  Pencil,
  Rocket,
  Ticket,
  Trash2,
  Trophy,
} from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';

import { ROUTES } from '@drawly/constants';

import { useRaffleTicketCounts } from '@/features/tickets';

import { useGenerateTickets, usePublishRaffle, useRegisterWinner } from '../hooks/use-raffles';
import { formatDrawDate } from '../services/format';
import { RAFFLE_STATUS_PRESENTATION } from '../services/raffle-status';

interface RaffleCardProps {
  raffle: RaffleDto;
  onEdit: (raffle: RaffleDto) => void;
  onDelete: (raffle: RaffleDto) => void;
  onDuplicate: (raffle: RaffleDto) => void;
}

export function RaffleCard({
  raffle,
  onEdit,
  onDelete,
  onDuplicate,
}: RaffleCardProps): React.JSX.Element {
  const generate = useGenerateTickets();
  const publish = usePublishRaffle();
  const registerWinner = useRegisterWinner();
  const winnerModal = useDisclosure();
  const [ticketNumber, setTicketNumber] = useState('');
  const { data: counts } = useRaffleTicketCounts(raffle.id);
  const actionError = generate.error ?? publish.error;

  const closeWinnerModal = (): void => {
    winnerModal.close();
    setTicketNumber('');
    registerWinner.reset();
  };

  const reserved = counts?.reserved ?? 0;
  const paid = counts?.paid ?? 0;
  const total = raffle.total_tickets;
  const soldPct = total > 0 ? (paid / total) * 100 : 0;
  // `counts` isn't loaded yet on first render — don't flash "sin generar"
  // for a raffle that already has tickets while the query is in flight.
  const ticketsGenerated = counts ? counts.generated > 0 : null;
  const presentation = RAFFLE_STATUS_PRESENTATION[raffle.status];
  const canViewPortal = raffle.status !== 'draft';
  // The backend hard-blocks publishing before this date (RaffleService.
  // ensure_can_publish) — mirrored here so the menu item doesn't invite a
  // click that only comes back as a 409.
  const isScheduledForLater = raffle.publish_at != null && new Date(raffle.publish_at) > new Date();

  return (
    <Card className="flex flex-col gap-4 p-5 transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 flex-col gap-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-text-primary truncate text-base font-semibold">{raffle.title}</p>
            <StatusBadge label={presentation.label} tone={presentation.tone} />
            {raffle.status === 'draft' && ticketsGenerated !== null && (
              <StatusBadge
                label={ticketsGenerated ? 'Boletas generadas' : 'Boletas sin generar'}
                tone={ticketsGenerated ? 'success' : 'warning'}
              />
            )}
          </div>
          <p className="text-text-secondary truncate text-sm">{raffle.prize}</p>
          <p className="text-text-muted flex items-center gap-1 text-xs">
            <Calendar size={12} /> Sorteo: {formatDrawDate(raffle.draw_date)}
          </p>
          {raffle.status === 'draft' && raffle.publish_at && (
            <p className="text-text-muted flex items-center gap-1 text-xs">
              <Clock size={12} /> Se activa: {formatDrawDate(raffle.publish_at)}
            </p>
          )}
        </div>

        <ActionMenu
          ariaLabel={`Más acciones para ${raffle.title}`}
          items={[
            { label: 'Editar', icon: <Pencil size={14} />, onSelect: () => onEdit(raffle) },
            {
              label: 'Publicar',
              icon: <Rocket size={14} />,
              onSelect: () => publish.mutate(raffle.id),
              disabled: raffle.status !== 'draft' || isScheduledForLater || !ticketsGenerated,
            },
            {
              label: 'Registrar ganador',
              icon: <Trophy size={14} />,
              onSelect: () => winnerModal.open(),
              disabled: raffle.status !== 'published',
            },
            {
              label: 'Ver portal',
              icon: <ExternalLink size={14} />,
              onSelect: () => window.open(ROUTES.PUBLIC_RAFFLE(raffle.public_slug), '_blank'),
              disabled: !canViewPortal,
            },
            { label: 'Duplicar', icon: <Copy size={14} />, onSelect: () => onDuplicate(raffle) },
            {
              label: 'Eliminar',
              icon: <Trash2 size={14} />,
              tone: 'danger',
              onSelect: () => onDelete(raffle),
            },
          ]}
        />
      </div>

      {actionError != null && (
        <Alert tone="danger">{getApiErrorMessage(actionError, 'La acción falló.')}</Alert>
      )}

      <div className="grid grid-cols-3 gap-3 text-center">
        <div>
          <p className="text-text-primary text-lg font-semibold">{total}</p>
          <p className="text-text-muted text-xs">Boletas</p>
        </div>
        <div>
          <p className="text-warning text-lg font-semibold">{reserved}</p>
          <p className="text-text-muted text-xs">Reservadas</p>
        </div>
        <div>
          <p className="text-success text-lg font-semibold">{paid}</p>
          <p className="text-text-muted text-xs">Pagadas</p>
        </div>
      </div>

      <ProgressBar value={soldPct} label="Vendido" tone="success" />

      <div className="border-border flex flex-wrap items-center gap-2 border-t pt-3">
        {raffle.status === 'draft' && !ticketsGenerated && (
          <Button
            variant="outline"
            size="sm"
            leftIcon={<Ticket size={14} />}
            loading={generate.isPending}
            onClick={() => generate.mutate(raffle.id)}
          >
            Generar boletas
          </Button>
        )}
        {canViewPortal && (
          <Link href={ROUTES.PUBLIC_RAFFLE(raffle.public_slug)} target="_blank">
            <Button variant="outline" size="sm" leftIcon={<ExternalLink size={14} />}>
              Página pública
            </Button>
          </Link>
        )}
        <Link href={ROUTES.RAFFLE_TICKETS(raffle.id)}>
          <Button variant="secondary" size="sm">
            Gestionar boletas
          </Button>
        </Link>
      </div>

      <Modal
        open={winnerModal.isOpen}
        onClose={closeWinnerModal}
        closeDisabled={registerWinner.isPending}
        title="Registrar ganador"
      >
        {registerWinner.data ? (
          registerWinner.data.valid ? (
            <div className="flex flex-col gap-4">
              <Alert tone="success">
                Boleta #{registerWinner.data.ticket_number} confirmada como ganadora. La rifa se
                cerró.
              </Alert>
              <Button onClick={closeWinnerModal}>Cerrar</Button>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              <Alert tone="warning">
                La boleta #{registerWinner.data.ticket_number} no está pagada, así que no se
                registró ganador. Puedes intentar con otro número.
              </Alert>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setTicketNumber('');
                    registerWinner.reset();
                  }}
                >
                  Intentar otro número
                </Button>
                <Button variant="ghost" onClick={closeWinnerModal}>
                  Cerrar
                </Button>
              </div>
            </div>
          )
        ) : (
          <form
            className="flex flex-col gap-4"
            onSubmit={(event) => {
              event.preventDefault();
              const number = Number(ticketNumber);
              if (!Number.isInteger(number) || number < 0) return;
              registerWinner.mutate({ id: raffle.id, payload: { ticket_number: number } });
            }}
          >
            <Field label="Número de boleta ganadora">
              <Input
                type="number"
                min={0}
                value={ticketNumber}
                onChange={(event) => setTicketNumber(event.target.value)}
                placeholder="Ej. 42"
                autoFocus
              />
            </Field>
            {registerWinner.isError && (
              <Alert tone="danger">
                {getApiErrorMessage(registerWinner.error, 'No se pudo registrar el ganador.')}
              </Alert>
            )}
            <Button type="submit" loading={registerWinner.isPending} disabled={!ticketNumber}>
              Confirmar
            </Button>
          </form>
        )}
      </Modal>
    </Card>
  );
}
