'use client';

import { Moon, Sun } from 'lucide-react';

import { IconButton } from './IconButton';
import { useTheme } from './theme';

export function ThemeToggle(): React.JSX.Element {
  const { theme, toggle } = useTheme();
  return (
    <IconButton
      variant="ghost"
      onClick={toggle}
      aria-label={theme === 'dark' ? 'Activar tema claro' : 'Activar tema oscuro'}
    >
      {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
    </IconButton>
  );
}
