'use client';

import { Ticket } from 'lucide-react';
import Link from 'next/link';
import type { ReactNode } from 'react';

import { ROUTES } from '@drawly/constants';
import { ThemeToggle } from '@drawly/ui/ThemeToggle';

interface AuthCardProps {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer: ReactNode;
}

/** Centered card used by the login and register screens. */
export function AuthCard({ title, subtitle, children, footer }: AuthCardProps): React.JSX.Element {
  return (
    <main className="bg-background text-text-primary relative flex min-h-screen items-center justify-center px-4 py-10">
      <div className="absolute right-4 top-4">
        <ThemeToggle />
      </div>

      <div className="flex w-full max-w-sm flex-col gap-6">
        <Link href={ROUTES.HOME} className="flex flex-col items-center gap-3">
          <span className="bg-primary text-primary-fg flex h-12 w-12 items-center justify-center rounded-2xl shadow-lg">
            <Ticket size={24} />
          </span>
          <span className="text-2xl font-semibold tracking-tight">Drawly</span>
        </Link>

        <div className="border-border bg-surface flex flex-col gap-5 rounded-2xl border p-6 shadow-sm">
          <div className="flex flex-col gap-1 text-center">
            <h1 className="text-xl font-semibold">{title}</h1>
            <p className="text-text-secondary text-sm">{subtitle}</p>
          </div>
          {children}
        </div>

        <p className="text-text-secondary text-center text-sm">{footer}</p>
      </div>
    </main>
  );
}
