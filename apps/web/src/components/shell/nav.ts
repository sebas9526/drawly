import {
  BarChart3,
  CreditCard,
  LayoutDashboard,
  Settings,
  Sparkles,
  UserCog,
  Users,
  type LucideIcon,
} from 'lucide-react';

import { ROUTES } from '@drawly/constants';

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

export const NAV_MAIN: NavItem[] = [
  { label: 'Dashboard', href: ROUTES.DASHBOARD, icon: LayoutDashboard },
  { label: 'Rifas', href: ROUTES.RAFFLES, icon: Sparkles },
  { label: 'Participantes', href: ROUTES.PARTICIPANTS, icon: Users },
  { label: 'Colaboradores', href: ROUTES.COLLABORATORS, icon: UserCog },
  { label: 'Reportes', href: ROUTES.REPORTS, icon: BarChart3 },
];

export const NAV_SOON: { label: string; icon: LucideIcon }[] = [
  { label: 'Pagos', icon: CreditCard },
  { label: 'Configuración', icon: Settings },
];
