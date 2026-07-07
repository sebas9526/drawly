'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import type { ReactNode } from 'react';

import { ROUTES } from '@drawly/constants';

import { useAuth } from '../hooks/use-auth';

/**
 * Wraps public entry pages (landing, login, register). Authenticated users are
 * sent straight to the dashboard; everyone else sees the page.
 */
export function RedirectAuthenticated({ children }: { children: ReactNode }): React.JSX.Element {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated) router.replace(ROUTES.DASHBOARD);
  }, [isAuthenticated, router]);

  return <>{children}</>;
}
