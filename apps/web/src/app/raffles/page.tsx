'use client';

import { AppShell } from '@/components/shell/app-shell';
import { RafflesAdmin } from '@/features/raffles';

export default function RafflesPage(): React.JSX.Element {
  return (
    <AppShell breadcrumbs={[{ label: 'Rifas' }]}>
      <RafflesAdmin />
    </AppShell>
  );
}
