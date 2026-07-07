'use client';

import { Card } from '@drawly/ui/Card';
import { cn } from '@drawly/utils';
import { ExternalLink, Plus, Receipt, UserCog, Users } from 'lucide-react';
import Link from 'next/link';

import { ROUTES } from '@drawly/constants';

interface QuickActionCardProps {
  label: string;
  icon: React.ReactNode;
  href?: string | undefined;
  onClick?: () => void;
  disabled?: boolean;
  external?: boolean;
}

function QuickActionCard({
  label,
  icon,
  href,
  onClick,
  disabled,
  external,
}: QuickActionCardProps): React.JSX.Element {
  const content = (
    <Card
      className={cn(
        'flex flex-col items-center gap-2 p-4 text-center transition-all',
        disabled
          ? 'pointer-events-none opacity-50'
          : 'cursor-pointer hover:-translate-y-0.5 hover:shadow-md',
      )}
    >
      <span className="bg-primary/10 text-primary flex h-10 w-10 items-center justify-center rounded-lg">
        {icon}
      </span>
      <span className="text-text-primary text-sm font-medium">{label}</span>
    </Card>
  );

  if (disabled) return content;

  if (href) {
    return (
      <Link href={href} target={external ? '_blank' : undefined} className="block">
        {content}
      </Link>
    );
  }

  return (
    <button type="button" onClick={onClick} className="block w-full text-left">
      {content}
    </button>
  );
}

interface QuickActionsProps {
  onCreateRaffle: () => void;
  publicRaffleHref: string | null;
}

/** Shortcut cards to the most common admin tasks — pure navigation, no new
 * business logic beyond opening the existing "create raffle" modal. */
export function QuickActions({
  onCreateRaffle,
  publicRaffleHref,
}: QuickActionsProps): React.JSX.Element {
  return (
    <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
      <QuickActionCard label="Nueva rifa" icon={<Plus size={18} />} onClick={onCreateRaffle} />
      <QuickActionCard
        label="Ver portal público"
        icon={<ExternalLink size={18} />}
        href={publicRaffleHref ?? undefined}
        external
        disabled={!publicRaffleHref}
      />
      <QuickActionCard
        label="Participantes"
        icon={<Users size={18} />}
        href={ROUTES.PARTICIPANTS}
      />
      <QuickActionCard
        label="Colaboradores"
        icon={<UserCog size={18} />}
        href={ROUTES.COLLABORATORS}
      />
      <QuickActionCard
        label="Ver reservas"
        icon={<Receipt size={18} />}
        href="#recent-reservations"
      />
    </section>
  );
}
