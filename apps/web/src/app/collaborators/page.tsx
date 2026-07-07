'use client';

import { AppShell } from '@/components/shell/app-shell';
import { CollaboratorsAdmin } from '@/features/collaborators';

export default function CollaboratorsPage(): React.JSX.Element {
  return (
    <AppShell breadcrumbs={[{ label: 'Colaboradores' }]}>
      <CollaboratorsAdmin />
    </AppShell>
  );
}
