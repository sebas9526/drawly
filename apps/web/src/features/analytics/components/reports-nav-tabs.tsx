'use client';

import { cn } from '@drawly/utils';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

import { ROUTES } from '@drawly/constants';

const REPORT_TABS = [
  { href: ROUTES.REPORTS, label: 'Resumen' },
  { href: ROUTES.REPORTS_RAFFLES, label: 'Rifas' },
  { href: ROUTES.REPORTS_COLLABORATORS, label: 'Colaboradores' },
  { href: ROUTES.REPORTS_PARTICIPANTS, label: 'Participantes' },
];

/** Route-based tabs between the four report pages — visually matches
 * `@drawly/ui/Tabs` but navigates instead of switching local state. */
export function ReportsNavTabs(): React.JSX.Element {
  const pathname = usePathname();

  return (
    <div className="border-border flex gap-1 border-b" role="tablist">
      {REPORT_TABS.map((tab) => {
        const active = pathname === tab.href;
        return (
          <Link
            key={tab.href}
            href={tab.href}
            role="tab"
            aria-selected={active}
            className={cn(
              '-mb-px border-b-2 px-3 py-2 text-sm font-medium transition-colors',
              active
                ? 'border-primary text-primary'
                : 'text-text-secondary hover:text-text-primary border-transparent',
            )}
          >
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}
