'use client';

import { Landing, RedirectAuthenticated } from '@/features/auth';

export default function HomePage(): React.JSX.Element {
  return (
    <RedirectAuthenticated>
      <Landing />
    </RedirectAuthenticated>
  );
}
