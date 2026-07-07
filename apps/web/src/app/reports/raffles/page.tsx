'use client';

import { ROUTES } from '@drawly/constants';

import { AppShell } from '@/components/shell/app-shell';
import { ReportsRaffles } from '@/features/analytics';

export default function ReportsRafflesPage(): React.JSX.Element {
  return (
    <AppShell
      breadcrumbs={[
        { label: 'Dashboard', href: ROUTES.DASHBOARD },
        { label: 'Reportes', href: ROUTES.REPORTS },
        { label: 'Rifas' },
      ]}
    >
      <ReportsRaffles />
    </AppShell>
  );
}
