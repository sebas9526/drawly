'use client';

import { ROUTES } from '@drawly/constants';

import { AppShell } from '@/components/shell/app-shell';
import { ReportsCollaborators } from '@/features/analytics';

export default function ReportsCollaboratorsPage(): React.JSX.Element {
  return (
    <AppShell
      breadcrumbs={[
        { label: 'Dashboard', href: ROUTES.DASHBOARD },
        { label: 'Reportes', href: ROUTES.REPORTS },
        { label: 'Colaboradores' },
      ]}
    >
      <ReportsCollaborators />
    </AppShell>
  );
}
