'use client';

import { useParams } from 'next/navigation';

import { ReferralPage } from '@/features/public-raffle';

export default function ReferralRoute(): React.JSX.Element {
  const params = useParams<{ collaboratorId: string }>();
  return <ReferralPage collaboratorId={params.collaboratorId} />;
}
