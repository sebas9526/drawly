'use client';

import { useEffect, useRef } from 'react';

import { cn } from '@drawly/utils';

import { useDisclosure } from './use-disclosure';

export interface DropdownItem {
  label: string;
  onSelect: () => void;
  icon?: React.ReactNode;
  tone?: 'default' | 'danger';
  disabled?: boolean;
}

interface DropdownProps {
  trigger: React.ReactNode;
  items: DropdownItem[];
  align?: 'left' | 'right';
  triggerClassName?: string;
  triggerAriaLabel?: string;
}

export function Dropdown({
  trigger,
  items,
  align = 'right',
  triggerClassName,
  triggerAriaLabel,
}: DropdownProps): React.JSX.Element {
  const { isOpen, toggle, close } = useDisclosure();
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const onClick = (event: MouseEvent): void => {
      if (ref.current && !ref.current.contains(event.target as Node)) close();
    };
    const onKey = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') close();
    };
    document.addEventListener('mousedown', onClick);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onClick);
      document.removeEventListener('keydown', onKey);
    };
  }, [isOpen, close]);

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={toggle}
        aria-haspopup="menu"
        aria-expanded={isOpen}
        aria-label={triggerAriaLabel}
        className={triggerClassName}
      >
        {trigger}
      </button>
      {isOpen && (
        <div
          role="menu"
          className={cn(
            'animate-fade-in-up bg-card border-border absolute z-50 mt-1 min-w-44 overflow-hidden rounded-lg border p-1 shadow-lg',
            align === 'right' ? 'right-0' : 'left-0',
          )}
        >
          {items.map((item, index) => (
            <button
              key={`${item.label}-${index}`}
              type="button"
              role="menuitem"
              disabled={item.disabled}
              onClick={() => {
                if (item.disabled) return;
                item.onSelect();
                close();
              }}
              className={cn(
                'flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-left text-sm transition-colors',
                item.disabled
                  ? 'text-text-muted pointer-events-none opacity-50'
                  : item.tone === 'danger'
                    ? 'text-danger hover:bg-danger/10'
                    : 'text-text-primary hover:bg-muted',
              )}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
