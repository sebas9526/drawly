'use client';

import { useQuery } from '@tanstack/react-query';

import { QUERY_KEYS } from '@drawly/constants';

import { api } from '@/lib/api';

export default function HomePage(): React.JSX.Element {
  const { data, isLoading, isError } = useQuery({
    queryKey: QUERY_KEYS.health,
    queryFn: () => api.health.check(),
  });

  const apiStatus = isLoading ? 'checking…' : isError ? 'unreachable' : data?.status;

  return (
    <main className="bg-background flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center">
      <h1 className="text-text-primary text-3xl font-semibold">Drawly</h1>
      <p className="text-text-secondary">Modern Raffle Management Platform</p>
      <p className="border-border bg-surface text-text-secondary rounded border px-4 py-2 text-sm">
        API status: <span className="text-text-primary font-medium">{apiStatus}</span>
      </p>
    </main>
  );
}
