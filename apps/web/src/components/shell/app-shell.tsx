'use client';

import { Menu, PanelLeftClose, PanelLeftOpen, Search, Ticket } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

import { ROUTES } from '@drawly/constants';
import { useLocalStorage } from '@drawly/hooks';
import { Avatar } from '@drawly/ui/Avatar';
import { Badge } from '@drawly/ui/Badge';
import { Breadcrumb, type BreadcrumbItem } from '@drawly/ui/Breadcrumb';
import { Dropdown } from '@drawly/ui/Dropdown';
import { IconButton } from '@drawly/ui/IconButton';
import { ThemeToggle } from '@drawly/ui/ThemeToggle';
import { cn } from '@drawly/utils';

import { RequireAuth, useAuth, useLogout } from '@/features/auth';

import { NAV_MAIN, NAV_SOON } from './nav';

const COLLAPSE_KEY = 'drawly-sidebar-collapsed';

function Logo({ collapsed }: { collapsed: boolean }): React.JSX.Element {
  return (
    <Link href={ROUTES.DASHBOARD} className="flex h-16 items-center gap-2 px-4">
      <span className="bg-primary text-primary-fg flex h-8 w-8 shrink-0 items-center justify-center rounded-lg">
        <Ticket size={18} />
      </span>
      {!collapsed && <span className="text-text-primary text-lg font-semibold">Drawly</span>}
    </Link>
  );
}

function SidebarNav({ collapsed }: { collapsed: boolean }): React.JSX.Element {
  const pathname = usePathname();
  return (
    <nav className="flex flex-1 flex-col gap-1 px-3 py-2">
      {NAV_MAIN.map((item) => {
        const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            title={collapsed ? item.label : undefined}
            className={cn(
              'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
              active
                ? 'bg-primary/10 text-primary'
                : 'text-text-secondary hover:bg-muted hover:text-text-primary',
            )}
          >
            <Icon size={18} className="shrink-0" />
            {!collapsed && item.label}
          </Link>
        );
      })}

      {!collapsed && (
        <p className="text-text-muted mt-4 px-3 pb-1 text-xs font-semibold uppercase tracking-wide">
          Próximamente
        </p>
      )}
      {NAV_SOON.map((item) => {
        const Icon = item.icon;
        return (
          <span
            key={item.label}
            title={collapsed ? `${item.label} (pronto)` : undefined}
            className="text-text-muted flex cursor-not-allowed items-center gap-3 rounded-lg px-3 py-2 text-sm"
          >
            <Icon size={18} className="shrink-0" />
            {!collapsed && (
              <span className="flex flex-1 items-center justify-between">
                {item.label}
                <Badge tone="neutral">Pronto</Badge>
              </span>
            )}
          </span>
        );
      })}
    </nav>
  );
}

interface AppShellProps {
  breadcrumbs?: BreadcrumbItem[];
  children: React.ReactNode;
}

function AppShellInner({ breadcrumbs, children }: AppShellProps): React.JSX.Element {
  const [collapsed, setCollapsed] = useLocalStorage(COLLAPSE_KEY, false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user } = useAuth();
  const logout = useLogout();

  const toggleCollapsed = (): void => setCollapsed(!collapsed);

  return (
    <div className="bg-background text-text-primary flex min-h-screen">
      {/* Desktop sidebar */}
      <aside
        className={cn(
          'border-border bg-surface hidden shrink-0 flex-col border-r transition-[width] md:flex',
          collapsed ? 'w-[68px]' : 'w-60',
        )}
      >
        <Logo collapsed={collapsed} />
        <SidebarNav collapsed={collapsed} />
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <button
            type="button"
            aria-label="Cerrar menú"
            className="animate-fade-in absolute inset-0 bg-neutral-950/50"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="border-border bg-surface animate-slide-in-right absolute inset-y-0 left-0 flex w-64 flex-col border-r">
            <Logo collapsed={false} />
            <SidebarNav collapsed={false} />
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-border bg-surface/80 sticky top-0 z-30 flex h-16 items-center gap-3 border-b px-4 backdrop-blur">
          <IconButton
            variant="ghost"
            aria-label="Abrir menú"
            className="md:hidden"
            onClick={() => setMobileOpen(true)}
          >
            <Menu size={18} />
          </IconButton>
          <IconButton
            variant="ghost"
            aria-label={collapsed ? 'Expandir menú' : 'Colapsar menú'}
            className="hidden md:inline-flex"
            onClick={toggleCollapsed}
          >
            {collapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
          </IconButton>

          <div className="relative hidden max-w-xs flex-1 sm:block">
            <Search
              size={16}
              className="text-text-muted pointer-events-none absolute left-3 top-1/2 -translate-y-1/2"
            />
            <input
              disabled
              placeholder="Buscar…"
              className="border-border bg-muted/50 text-text-secondary placeholder:text-text-muted h-9 w-full rounded-lg border pl-9 pr-3 text-sm"
            />
          </div>

          <div className="ml-auto flex items-center gap-2">
            {user && (
              <span className="text-text-secondary hidden text-sm sm:inline">{user.full_name}</span>
            )}
            <ThemeToggle />
            <Dropdown
              align="right"
              trigger={<Avatar name={user?.full_name ?? 'Cuenta'} size="sm" />}
              items={[{ label: 'Cerrar sesión', onSelect: () => logout.mutate(), tone: 'danger' }]}
            />
          </div>
        </header>

        <main className="flex-1 p-4 sm:p-6">
          <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
            {breadcrumbs && breadcrumbs.length > 0 && <Breadcrumb items={breadcrumbs} />}
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

/**
 * Admin shell. Wraps every private page in {@link RequireAuth}, so the Dashboard
 * and all admin surfaces are never reachable without an authenticated session.
 */
export function AppShell(props: AppShellProps): React.JSX.Element {
  return (
    <RequireAuth>
      <AppShellInner {...props} />
    </RequireAuth>
  );
}
