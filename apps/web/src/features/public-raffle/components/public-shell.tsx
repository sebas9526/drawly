'use client';

import { ThemeToggle } from '@drawly/ui/ThemeToggle';
import { Ticket } from 'lucide-react';

/** Shared header/layout for every public-portal page (raffle page, referral
 * link picker) — kept as one component so they stay visually consistent. */
export function PublicShell({ children }: { children: React.ReactNode }): React.JSX.Element {
  return (
    <div className="bg-background text-text-primary min-h-screen">
      <header className="border-border bg-surface/80 sticky top-0 z-20 border-b backdrop-blur">
        <div className="mx-auto flex h-14 w-full max-w-3xl items-center justify-between px-6">
          <span className="text-text-primary flex items-center gap-2 font-semibold">
            <span className="bg-primary text-primary-fg flex h-7 w-7 items-center justify-center rounded-lg">
              <Ticket size={16} />
            </span>
            Drawly
          </span>
          <ThemeToggle />
        </div>
      </header>
      <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">{children}</main>
    </div>
  );
}
