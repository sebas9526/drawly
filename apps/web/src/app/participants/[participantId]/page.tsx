'use client';

import { useParams } from 'next/navigation';

import { ROUTES } from '@drawly/constants';

import { AppShell } from '@/components/shell/app-shell';
import { ParticipantDetail } from '@/features/participants';

export default function ParticipantDetailPage(): React.JSX.Element {
  const params = useParams<{ participantId: string }>();
  return (
    <AppShell
      breadcrumbs={[{ label: 'Participantes', href: ROUTES.PARTICIPANTS }, { label: 'Detalle' }]}
    >
      <ParticipantDetail participantId={params.participantId} />
    </AppShell>
  );
}
