'use client';

import { useParams } from 'next/navigation';

import { PublicRafflePage } from '@/features/public-raffle';

export default function PublicRaffleRoute(): React.JSX.Element {
  const params = useParams<{ slug: string }>();
  return <PublicRafflePage slug={params.slug} />;
}
