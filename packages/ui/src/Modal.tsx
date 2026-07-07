'use client';

import { X } from 'lucide-react';
import { useEffect } from 'react';

import { cn } from '@drawly/utils';

import { IconButton } from './IconButton';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
}

export function Modal({
  open,
  onClose,
  title,
  children,
  footer,
  className,
}: ModalProps): React.JSX.Element | null {
  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <button
        type="button"
        aria-label="Cerrar"
        className="animate-fade-in absolute inset-0 bg-neutral-950/60"
        onClick={onClose}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={cn(
          'animate-scale-in bg-card border-border relative z-10 w-full max-w-md rounded-xl border p-5 shadow-xl',
          className,
        )}
      >
        <div className="mb-3 flex items-center justify-between gap-4">
          <h2 className="text-text-primary text-base font-semibold">{title}</h2>
          <IconButton size="sm" variant="ghost" aria-label="Cerrar" onClick={onClose}>
            <X size={16} />
          </IconButton>
        </div>
        <div>{children}</div>
        {footer && <div className="mt-5 flex justify-end gap-2">{footer}</div>}
      </div>
    </div>
  );
}
