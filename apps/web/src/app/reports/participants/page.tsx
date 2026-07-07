'use client';

import { ROUTES } from '@drawly/constants';

import { AppShell } from '@/components/shell/app-shell';
import { ReportsParticipants } from '@/features/analytics';

export default function ReportsParticipantsPage(): React.JSX.Element {
  return (
    <AppShell
      breadcrumbs={[
        { label: 'Dashboard', href: ROUTES.DASHBOARD },
        { label: 'Reportes', href: ROUTES.REPORTS },
        { label: 'Participantes' },
      ]}
    >
      <ReportsParticipants />
    </AppShell>
  );
}
