'use client';

import { ROUTES } from '@drawly/constants';

import { AppShell } from '@/components/shell/app-shell';
import { ReportsSummary } from '@/features/analytics';

export default function ReportsPage(): React.JSX.Element {
  return (
    <AppShell breadcrumbs={[{ label: 'Dashboard', href: ROUTES.DASHBOARD }, { label: 'Reportes' }]}>
      <ReportsSummary />
    </AppShell>
  );
}
