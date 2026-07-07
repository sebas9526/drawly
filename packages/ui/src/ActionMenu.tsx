'use client';

import { MoreVertical } from 'lucide-react';

import { Dropdown, type DropdownItem } from './Dropdown';
import { iconButtonClassName } from './IconButton';

interface ActionMenuProps {
  items: DropdownItem[];
  ariaLabel?: string;
  align?: 'left' | 'right';
}

/** Contextual "•••" action menu. Visually matches IconButton without nesting
 * two `<button>` elements inside Dropdown's own trigger wrapper. */
export function ActionMenu({
  items,
  ariaLabel = 'Más acciones',
  align = 'right',
}: ActionMenuProps): React.JSX.Element {
  return (
    <Dropdown
      align={align}
      triggerAriaLabel={ariaLabel}
      triggerClassName={iconButtonClassName('ghost', 'sm')}
      trigger={<MoreVertical size={16} />}
      items={items}
    />
  );
}
