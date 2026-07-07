'use client';

import { isApiError, type ParticipantDto } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Badge } from '@drawly/ui/Badge';
import { Card } from '@drawly/ui/Card';
import { ConfirmDialog } from '@drawly/ui/ConfirmDialog';
import { DataTable, type Column } from '@drawly/ui/DataTable';
import { IconButton } from '@drawly/ui/IconButton';
import { StatusBadge } from '@drawly/ui/StatusBadge';
import { Eye, Pencil, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';

import { ROUTES } from '@drawly/constants';

interface ParticipantTableProps {
  participants: ParticipantDto[];
  deletingId: string | null;
  deleteError: unknown;
  onEdit: (participant: ParticipantDto) => void;
  onDelete: (id: string) => void;
}

export function ParticipantTable({
  participants,
  deletingId,
  deleteError,
  onEdit,
  onDelete,
}: ParticipantTableProps): React.JSX.Element {
  const [confirming, setConfirming] = useState<ParticipantDto | null>(null);

  const columns: Column<ParticipantDto>[] = [
    {
      key: 'name',
      header: 'Nombre',
      sortable: true,
      sortValue: (p) => p.full_name,
      render: (p) => <span className="font-medium">{p.full_name}</span>,
    },
    { key: 'phone', header: 'Teléfono', render: (p) => p.phone },
    { key: 'document', header: 'Documento', render: (p) => p.document ?? '—' },
    { key: 'city', header: 'Ciudad', render: (p) => p.city ?? '—' },
    {
      key: 'tickets',
      header: 'Boletas',
      sortable: true,
      sortValue: (p) => p.ticket_count,
      render: (p) => (
        <Badge tone={p.ticket_count > 0 ? 'primary' : 'neutral'}>{p.ticket_count}</Badge>
      ),
    },
    {
      key: 'status',
      header: 'Estado',
      sortable: true,
      sortValue: (p) => (p.ticket_count > 0 ? 1 : 0),
      render: (p) =>
        p.ticket_count > 0 ? (
          <StatusBadge label="Con boletas" tone="success" />
        ) : (
          <StatusBadge label="Sin boletas" tone="neutral" />
        ),
    },
    {
      key: 'actions',
      header: '',
      render: (p) => (
        <div className="flex justify-end gap-1">
          <Link href={ROUTES.PARTICIPANT_DETAIL(p.id)}>
            <IconButton size="sm" variant="ghost" aria-label="Ver detalle">
              <Eye size={16} />
            </IconButton>
          </Link>
          <IconButton size="sm" variant="ghost" aria-label="Editar" onClick={() => onEdit(p)}>
            <Pencil size={16} />
          </IconButton>
          <IconButton
            size="sm"
            variant="danger"
            aria-label="Eliminar"
            disabled={deletingId === p.id}
            onClick={() => setConfirming(p)}
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
          {isApiError(deleteError) ? deleteError.message : 'No se pudo eliminar el participante.'}
        </Alert>
      )}
      <Card className="p-2 sm:p-4">
        <DataTable columns={columns} rows={participants} getRowKey={(p) => p.id} pageSize={10} />
      </Card>

      <ConfirmDialog
        open={confirming !== null}
        onClose={() => setConfirming(null)}
        onConfirm={() => {
          if (confirming) onDelete(confirming.id);
          setConfirming(null);
        }}
        title="Eliminar participante"
        description={
          confirming
            ? `¿Seguro que quieres eliminar a ${confirming.full_name}? No se puede eliminar si tiene boletas asignadas.`
            : undefined
        }
        confirmLabel="Eliminar"
        tone="danger"
        loading={confirming !== null && deletingId === confirming.id}
      />
    </div>
  );
}
