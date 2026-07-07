'use client';

import type { PublicRaffleView } from '@drawly/api-client';
import { Card } from '@drawly/ui/Card';
import { Gift } from 'lucide-react';

function Stat({ label, value }: { label: string; value: number }): React.JSX.Element {
  return (
    <div className="bg-muted/60 rounded-lg px-3 py-2 text-center">
      <p className="text-text-primary text-lg font-semibold">{value}</p>
      <p className="text-text-secondary text-xs">{label}</p>
    </div>
  );
}

export function RaffleHeader({ raffle }: { raffle: PublicRaffleView }): React.JSX.Element {
  const drawDate = new Date(raffle.draw_date).toLocaleString('es-CO', {
    dateStyle: 'medium',
    timeStyle: 'short',
  });

  return (
    <Card className="flex flex-col gap-5 overflow-hidden">
      {raffle.cover_image ? (
        <div
          className="h-52 w-full bg-cover bg-center"
          style={{ backgroundImage: `url(${raffle.cover_image})` }}
          role="img"
          aria-label={raffle.title}
        />
      ) : (
        <div className="bg-primary/10 text-primary flex h-40 w-full items-center justify-center">
          <Gift size={44} />
        </div>
      )}

      <div className="flex flex-col gap-5 p-5 pt-0">
        <div className="flex flex-col gap-1">
          <h1 className="text-text-primary text-2xl font-semibold">{raffle.title}</h1>
          <p className="text-text-secondary text-sm">{raffle.description}</p>
        </div>

        <dl className="text-text-secondary grid grid-cols-1 gap-2 text-sm sm:grid-cols-2">
          <div>
            <span className="text-text-primary font-medium">Premio:</span> {raffle.prize}
          </div>
          <div>
            <span className="text-text-primary font-medium">Precio por boleta:</span>{' '}
            {raffle.ticket_price}
          </div>
          <div>
            <span className="text-text-primary font-medium">Sorteo:</span> {drawDate}
          </div>
          <div>
            <span className="text-text-primary font-medium">Boletas:</span> {raffle.total_tickets}
          </div>
        </dl>

        <div className="grid grid-cols-4 gap-2">
          <Stat label="Total" value={raffle.total_tickets} />
          <Stat label="Disponibles" value={raffle.available_count} />
          <Stat label="Reservadas" value={raffle.reserved_count} />
          <Stat label="Pagadas" value={raffle.paid_count} />
        </div>
      </div>
    </Card>
  );
}
