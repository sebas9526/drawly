'use client';

import { getApiErrorMessage } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Avatar } from '@drawly/ui/Avatar';
import { Card } from '@drawly/ui/Card';
import { DashboardCard } from '@drawly/ui/DashboardCard';
import { EmptyState } from '@drawly/ui/EmptyState';
import { Loader } from '@drawly/ui/Loader';
import { StatusBadge } from '@drawly/ui/StatusBadge';
import { Ticket } from 'lucide-react';
import { useMemo } from 'react';

import { useRaffles } from '@/features/raffles';
import { TICKET_STATUS_PRESENTATION } from '@/features/tickets';

import { useParticipant, useParticipantTickets } from '../hooks/use-participants';

interface ParticipantDetailProps {
  participantId: string;
}

function InfoRow({ label, value }: { label: string; value: string }): React.JSX.Element {
  return (
    <div className="flex justify-between gap-4 text-sm">
      <span className="text-text-secondary">{label}</span>
      <span className="text-text-primary text-right font-medium">{value}</span>
    </div>
  );
}

export function ParticipantDetail({ participantId }: ParticipantDetailProps): React.JSX.Element {
  const { data: participant, isLoading, isError, error } = useParticipant(participantId);
  const { data: tickets } = useParticipantTickets(participantId);
  const { data: raffles } = useRaffles();

  const raffleTitle = useMemo(() => {
    const map = new Map<string, string>();
    raffles?.forEach((raffle) => map.set(raffle.id, raffle.title));
    return (id: string): string => map.get(id) ?? id;
  }, [raffles]);

  if (isLoading) return <Loader />;
  if (isError || !participant) {
    return (
      <Alert tone="danger" title="No pudimos cargar el participante">
        {getApiErrorMessage(error, 'Intenta de nuevo más tarde.')}
      </Alert>
    );
  }

  return (
    <>
      <div className="flex items-center gap-4">
        <Avatar name={participant.full_name} />
        <div>
          <h1 className="text-text-primary text-2xl font-semibold">{participant.full_name}</h1>
          <p className="text-text-secondary text-sm">{participant.phone}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="flex flex-col gap-3 p-5 lg:col-span-1">
          <InfoRow label="Correo" value={participant.email ?? '—'} />
          <InfoRow label="Documento" value={participant.document ?? '—'} />
          <InfoRow label="Ciudad" value={participant.city ?? '—'} />
          <InfoRow label="Dirección" value={participant.address ?? '—'} />
          {participant.notes && <InfoRow label="Notas" value={participant.notes} />}
        </Card>

        <DashboardCard title="Boletas" className="lg:col-span-2">
          {!tickets || tickets.length === 0 ? (
            <EmptyState
              icon={<Ticket size={26} />}
              title="Sin boletas"
              description="Este participante aún no tiene boletas asignadas."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-left text-sm">
                <thead>
                  <tr className="text-text-secondary border-border border-b">
                    <th className="py-2.5 pr-4 font-medium">Número</th>
                    <th className="py-2.5 pr-4 font-medium">Estado</th>
                    <th className="py-2.5 font-medium">Rifa</th>
                  </tr>
                </thead>
                <tbody>
                  {tickets.map((ticket) => (
                    <tr key={ticket.id} className="border-border/60 border-b">
                      <td className="text-text-primary py-2.5 pr-4 font-mono">{ticket.number}</td>
                      <td className="py-2.5 pr-4">
                        <StatusBadge
                          label={TICKET_STATUS_PRESENTATION[ticket.status].label}
                          tone={TICKET_STATUS_PRESENTATION[ticket.status].tone}
                        />
                      </td>
                      <td className="text-text-secondary py-2.5">
                        {raffleTitle(ticket.raffle_id)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </DashboardCard>
      </div>
    </>
  );
}
