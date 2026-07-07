'use client';

import { AppShell } from '@/components/shell/app-shell';
import { ParticipantsAdmin } from '@/features/participants';

export default function ParticipantsPage(): React.JSX.Element {
  return (
    <AppShell breadcrumbs={[{ label: 'Participantes' }]}>
      <ParticipantsAdmin />
    </AppShell>
  );
}
