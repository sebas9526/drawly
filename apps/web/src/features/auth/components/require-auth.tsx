'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import type { ReactNode } from 'react';

import { ROUTES } from '@drawly/constants';
import { Spinner } from '@drawly/ui/Spinner';

import { useAuth } from '../hooks/use-auth';

/**
 * Route guard for private pages. While the session is being resolved it shows a
 * spinner; if the user is not authenticated it redirects to /login and renders
 * nothing (the Dashboard is never public).
 */
export function RequireAuth({ children }: { children: ReactNode }): React.JSX.Element | null {
  const { isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace(ROUTES.LOGIN);
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="bg-background flex min-h-screen items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return <>{children}</>;
}
