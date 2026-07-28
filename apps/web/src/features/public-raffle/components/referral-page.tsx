'use client';

import { isApiError } from '@drawly/api-client';
import { Card } from '@drawly/ui/Card';
import { EmptyState } from '@drawly/ui/EmptyState';
import { Skeleton } from '@drawly/ui/Skeleton';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

import { ROUTES } from '@drawly/constants';

import { usePublicReferralRaffles } from '../hooks/use-public-raffle';
import { PublicShell } from './public-shell';

/** Landing page for a collaborator's personal referral link
 * (/ref/{collaboratorId}): one raffle -> straight to reserving; several ->
 * a pick-one list; none/invalid -> a clear empty state. The actual
 * reservation flow (including the `?ref=` attribution) is unchanged —
 * PublicRafflePage already reads `?ref=` today. */
export function ReferralPage({ collaboratorId }: { collaboratorId: string }): React.JSX.Element {
  const query = usePublicReferralRaffles(collaboratorId);
  const router = useRouter();
  const raffles = query.data;
  const singleSlug = raffles?.length === 1 ? raffles[0]?.public_slug : null;

  useEffect(() => {
    if (!singleSlug) return;
    router.replace(`${ROUTES.PUBLIC_RAFFLE(singleSlug)}?ref=${collaboratorId}`);
  }, [singleSlug, collaboratorId, router]);

  if (query.isLoading || singleSlug) {
    return (
      <PublicShell>
        <Skeleton className="h-40 w-full" />
      </PublicShell>
    );
  }

  if (query.isError) {
    return (
      <PublicShell>
        <EmptyState
          title="Este link no es válido"
          description={
            isApiError(query.error)
              ? 'Puede que el vendedor ya no esté activo.'
              : 'No pudimos cargar este link. Intenta de nuevo más tarde.'
          }
        />
      </PublicShell>
    );
  }

  if (!raffles || raffles.length === 0) {
    return (
      <PublicShell>
        <EmptyState
          title="Sin rifas activas"
          description="Este vendedor no tiene rifas activas en este momento."
        />
      </PublicShell>
    );
  }

  return (
    <PublicShell>
      <p className="text-text-secondary text-sm">¿Para cuál rifa es tu boleta?</p>
      <div className="flex flex-col gap-3">
        {raffles.map((raffle) => (
          <a
            key={raffle.public_slug}
            href={`${ROUTES.PUBLIC_RAFFLE(raffle.public_slug)}?ref=${collaboratorId}`}
          >
            <Card className="hover:border-primary/40 flex items-center justify-between gap-3 p-4 transition-colors">
              <div>
                <p className="text-text-primary font-semibold">{raffle.title}</p>
                <p className="text-text-secondary text-sm">{raffle.prize}</p>
              </div>
            </Card>
          </a>
        ))}
      </div>
    </PublicShell>
  );
}
