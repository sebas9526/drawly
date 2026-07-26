'use client';

import { getApiErrorMessage, type RaffleDto } from '@drawly/api-client';
import { ActionMenu } from '@drawly/ui/ActionMenu';
import { Alert } from '@drawly/ui/Alert';
import { Button } from '@drawly/ui/Button';
import { Card } from '@drawly/ui/Card';
import { ProgressBar } from '@drawly/ui/ProgressBar';
import { StatusBadge } from '@drawly/ui/StatusBadge';
import { Calendar, Copy, ExternalLink, Pencil, Rocket, Ticket, Trash2 } from 'lucide-react';
import Link from 'next/link';

import { ROUTES } from '@drawly/constants';

import { useRaffleTicketCounts } from '@/features/tickets';

import { useGenerateTickets, usePublishRaffle } from '../hooks/use-raffles';
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
  const { data: counts } = useRaffleTicketCounts(raffle.id);
  const actionError = generate.error ?? publish.error;

  const reserved = counts?.reserved ?? 0;
  const paid = counts?.paid ?? 0;
  const total = raffle.total_tickets;
  const soldPct = total > 0 ? (paid / total) * 100 : 0;
  const presentation = RAFFLE_STATUS_PRESENTATION[raffle.status];
  const canViewPortal = raffle.status !== 'draft';

  return (
    <Card className="flex flex-col gap-4 p-5 transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 flex-col gap-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-text-primary truncate text-base font-semibold">{raffle.title}</p>
            <StatusBadge label={presentation.label} tone={presentation.tone} />
          </div>
          <p className="text-text-secondary truncate text-sm">{raffle.prize}</p>
          <p className="text-text-muted flex items-center gap-1 text-xs">
            <Calendar size={12} /> Sorteo: {formatDrawDate(raffle.draw_date)}
          </p>
        </div>

        <ActionMenu
          ariaLabel={`Más acciones para ${raffle.title}`}
          items={[
            { label: 'Editar', icon: <Pencil size={14} />, onSelect: () => onEdit(raffle) },
            {
              label: 'Publicar',
              icon: <Rocket size={14} />,
              onSelect: () => publish.mutate(raffle.id),
              disabled: raffle.status !== 'draft',
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
        {raffle.status === 'draft' && (
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
    </Card>
  );
}
