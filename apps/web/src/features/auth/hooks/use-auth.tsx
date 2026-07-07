'use client';

import type { AuthUser } from '@drawly/api-client';
import { useQuery } from '@tanstack/react-query';
import { createContext, useContext, useMemo } from 'react';
import type { ReactNode } from 'react';

import { QUERY_KEYS } from '@drawly/constants';

import { api } from '@/lib/api';

interface AuthContextValue {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Loads the current user once (via the session cookie) and shares it. A 401 is
 * expected when logged out, so the query never retries and simply resolves to
 * "not authenticated".
 */
export function AuthProvider({ children }: { children: ReactNode }): React.JSX.Element {
  const query = useQuery({
    queryKey: QUERY_KEYS.authMe,
    queryFn: () => api.auth.me(),
    retry: false,
    staleTime: 60_000,
    refetchOnWindowFocus: false,
  });

  const value = useMemo<AuthContextValue>(
    () => ({
      user: query.data ?? null,
      isLoading: query.isLoading,
      isAuthenticated: Boolean(query.data),
    }),
    [query.data, query.isLoading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (ctx === null) throw new Error('useAuth must be used within an AuthProvider.');
  return ctx;
}
