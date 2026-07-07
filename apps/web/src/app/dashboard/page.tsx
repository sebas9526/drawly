'use client';

import { AppShell } from '@/components/shell/app-shell';
import { DashboardPage } from '@/features/dashboard';

export default function DashboardRoute(): React.JSX.Element {
  return (
    <AppShell breadcrumbs={[{ label: 'Dashboard' }]}>
      <DashboardPage />
    </AppShell>
  );
}
