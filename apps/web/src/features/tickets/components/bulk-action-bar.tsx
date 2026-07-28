'use client';

import type { CollaboratorDto } from '@drawly/api-client';
import { Button } from '@drawly/ui/Button';
import { Select } from '@drawly/ui/Select';
import { Ban, CheckCheck, UserCog, Wallet, X } from 'lucide-react';
import { useState } from 'react';

interface BulkActionBarProps {
  selectedCount: number;
  collaborators: CollaboratorDto[];
  isPending: boolean;
  /** False while the raffle isn't published yet — see TicketTable's prop of
   * the same name for why Reservar/Marcar pagadas are disabled here too. */
  raffleIsOpen: boolean;
  onReserve: () => void;
  onCancel: () => void;
  onMarkPaid: () => void;
  onSetCollaborator: (collaboratorId: string) => void;
  onClearSelection: () => void;
}

/** Bulk actions for the tickets screen's multi-select. Each button applies the
 * same single-ticket transition to every selected row (see useBulkTicketActions). */
export function BulkActionBar({
  selectedCount,
  collaborators,
  isPending,
  raffleIsOpen,
  onReserve,
  onCancel,
  onMarkPaid,
  onSetCollaborator,
  onClearSelection,
}: BulkActionBarProps): React.JSX.Element {
  const [collaboratorId, setCollaboratorId] = useState('');

  return (
    <div className="bg-primary/5 border-primary/20 animate-fade-in-up flex flex-wrap items-center gap-3 rounded-lg border p-3">
      <span className="text-text-primary text-sm font-medium">
        {selectedCount} {selectedCount === 1 ? 'boleta seleccionada' : 'boletas seleccionadas'}
      </span>

      <div className="flex flex-wrap items-center gap-2">
        <Button
          size="sm"
          variant="outline"
          leftIcon={<CheckCheck size={14} />}
          disabled={isPending || !raffleIsOpen}
          onClick={onReserve}
        >
          Reservar
        </Button>
        <Button
          size="sm"
          variant="outline"
          leftIcon={<Ban size={14} />}
          disabled={isPending}
          onClick={onCancel}
        >
          Cancelar
        </Button>
        <Button
          size="sm"
          variant="outline"
          leftIcon={<Wallet size={14} />}
          disabled={isPending || !raffleIsOpen}
          onClick={onMarkPaid}
        >
          Marcar pagadas
        </Button>
        <div className="flex items-center gap-1.5">
          <Select
            className="w-40"
            aria-label="Colaborador"
            value={collaboratorId}
            disabled={isPending}
            onChange={(event) => setCollaboratorId(event.target.value)}
          >
            <option value="">— colaborador —</option>
            {collaborators.map((collaborator) => (
              <option key={collaborator.id} value={collaborator.id}>
                {collaborator.name}
              </option>
            ))}
          </Select>
          <Button
            size="sm"
            variant="outline"
            leftIcon={<UserCog size={14} />}
            disabled={isPending || !collaboratorId}
            onClick={() => onSetCollaborator(collaboratorId)}
          >
            Aplicar
          </Button>
        </div>
      </div>

      <Button
        size="sm"
        variant="ghost"
        leftIcon={<X size={14} />}
        className="ml-auto"
        onClick={onClearSelection}
      >
        Cancelar selección
      </Button>
    </div>
  );
}
