'use client';

import { getApiErrorMessage, type CollaboratorDto } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Card } from '@drawly/ui/Card';
import { ConfirmDialog } from '@drawly/ui/ConfirmDialog';
import { DataTable, type Column } from '@drawly/ui/DataTable';
import { IconButton } from '@drawly/ui/IconButton';
import { Switch } from '@drawly/ui/Switch';
import { Tooltip } from '@drawly/ui/Tooltip';
import { Check, Link2, Pencil, Trash2 } from 'lucide-react';
import { useState } from 'react';

interface CollaboratorTableProps {
  collaborators: CollaboratorDto[];
  raffleNameById: (raffleId: string) => string;
  deletingId: string | null;
  deleteError: unknown;
  onEdit: (collaborator: CollaboratorDto) => void;
  onToggleActive: (collaborator: CollaboratorDto) => void;
  onDelete: (id: string) => void;
  /** Copies the collaborator's referral link to the clipboard; returns false
   * when the raffle has no public slug yet (e.g. still a draft). */
  onCopyLink: (collaborator: CollaboratorDto) => Promise<boolean>;
}

export function CollaboratorTable({
  collaborators,
  raffleNameById,
  deletingId,
  deleteError,
  onEdit,
  onToggleActive,
  onDelete,
  onCopyLink,
}: CollaboratorTableProps): React.JSX.Element {
  const [confirming, setConfirming] = useState<CollaboratorDto | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = async (collaborator: CollaboratorDto): Promise<void> => {
    const copied = await onCopyLink(collaborator);
    if (!copied) return;
    setCopiedId(collaborator.id);
    setTimeout(
      () => setCopiedId((current) => (current === collaborator.id ? null : current)),
      1500,
    );
  };

  const columns: Column<CollaboratorDto>[] = [
    {
      key: 'name',
      header: 'Colaborador',
      sortable: true,
      sortValue: (c) => c.name,
      render: (c) => (
        <span className="flex items-center gap-2 font-medium">
          <span
            className="inline-block h-3 w-3 shrink-0 rounded-full"
            style={{ backgroundColor: c.color }}
            aria-hidden
          />
          {c.name}
        </span>
      ),
    },
    { key: 'raffle', header: 'Rifa', render: (c) => raffleNameById(c.raffle_id) },
    { key: 'phone', header: 'Teléfono', render: (c) => c.phone ?? '—' },
    { key: 'email', header: 'Correo', render: (c) => c.email ?? '—' },
    {
      key: 'active',
      header: 'Activo',
      sortable: true,
      sortValue: (c) => (c.is_active ? 1 : 0),
      render: (c) => (
        <Switch
          checked={c.is_active}
          onCheckedChange={() => onToggleActive(c)}
          aria-label={c.is_active ? 'Desactivar' : 'Activar'}
        />
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (c) => (
        <div className="flex justify-end gap-1">
          <Tooltip label={copiedId === c.id ? 'Copiado' : 'Copiar link de referido'}>
            <IconButton
              size="sm"
              variant="ghost"
              aria-label="Copiar link de referido"
              onClick={() => void handleCopy(c)}
            >
              {copiedId === c.id ? (
                <Check size={16} className="text-success" />
              ) : (
                <Link2 size={16} />
              )}
            </IconButton>
          </Tooltip>
          <IconButton size="sm" variant="ghost" aria-label="Editar" onClick={() => onEdit(c)}>
            <Pencil size={16} />
          </IconButton>
          <IconButton
            size="sm"
            variant="danger"
            aria-label="Eliminar"
            disabled={deletingId === c.id}
            onClick={() => setConfirming(c)}
          >
            <Trash2 size={16} />
          </IconButton>
        </div>
      ),
    },
  ];

  return (
    <div className="flex flex-col gap-3">
      {deleteError != null && (
        <Alert tone="danger">
          {getApiErrorMessage(deleteError, 'No se pudo eliminar el colaborador.')}
        </Alert>
      )}
      <Card className="p-2 sm:p-4">
        <DataTable columns={columns} rows={collaborators} getRowKey={(c) => c.id} pageSize={10} />
      </Card>

      <ConfirmDialog
        open={confirming !== null}
        onClose={() => setConfirming(null)}
        onConfirm={() => {
          if (confirming) onDelete(confirming.id);
          setConfirming(null);
        }}
        title="Eliminar colaborador"
        description={
          confirming
            ? `¿Seguro que quieres eliminar a ${confirming.name}? Las boletas que vendió conservarán el registro.`
            : undefined
        }
        confirmLabel="Eliminar"
        tone="danger"
        loading={confirming !== null && deletingId === confirming.id}
      />
    </div>
  );
}
