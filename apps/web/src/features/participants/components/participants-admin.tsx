'use client';

import { getApiErrorMessage, type ParticipantDto } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Button } from '@drawly/ui/Button';
import { EmptyState } from '@drawly/ui/EmptyState';
import { FilterTabs } from '@drawly/ui/FilterTabs';
import { Loader } from '@drawly/ui/Loader';
import { Modal } from '@drawly/ui/Modal';
import { PageHeader } from '@drawly/ui/PageHeader';
import { SearchInput } from '@drawly/ui/SearchInput';
import { useDisclosure } from '@drawly/ui/use-disclosure';
import { Plus, Users } from 'lucide-react';
import { useMemo, useState } from 'react';

import { useDeleteParticipant, useParticipants } from '../hooks/use-participants';
import { ParticipantForm } from './participant-form';
import { ParticipantTable } from './participant-table';

type StatusFilter = 'all' | 'with-tickets' | 'without-tickets';

export function ParticipantsAdmin(): React.JSX.Element {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [editing, setEditing] = useState<ParticipantDto | null>(null);
  const form = useDisclosure();

  const { data, isLoading, isError, error } = useParticipants(search.trim() || undefined);
  const deleteParticipant = useDeleteParticipant();

  const counts = useMemo(() => {
    const all = data ?? [];
    return {
      all: all.length,
      withTickets: all.filter((p) => p.ticket_count > 0).length,
      withoutTickets: all.filter((p) => p.ticket_count === 0).length,
    };
  }, [data]);

  const filtered = useMemo(() => {
    const all = data ?? [];
    if (statusFilter === 'with-tickets') return all.filter((p) => p.ticket_count > 0);
    if (statusFilter === 'without-tickets') return all.filter((p) => p.ticket_count === 0);
    return all;
  }, [data, statusFilter]);

  const openCreate = (): void => {
    setEditing(null);
    form.open();
  };
  const openEdit = (participant: ParticipantDto): void => {
    setEditing(participant);
    form.open();
  };
  const closeForm = (): void => {
    form.close();
    setEditing(null);
  };

  return (
    <>
      <PageHeader
        title="Participantes"
        description={`Administra las personas que reservan boletas. ${counts.all} en total.`}
        actions={
          <Button leftIcon={<Plus size={16} />} onClick={openCreate}>
            Nuevo participante
          </Button>
        }
      />

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <SearchInput
          containerClassName="max-w-md flex-1"
          placeholder="Buscar por nombre, teléfono, documento o correo"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <FilterTabs
          aria-label="Filtrar participantes por estado"
          value={statusFilter}
          onChange={setStatusFilter}
          options={[
            { value: 'all', label: 'Todos', count: counts.all },
            { value: 'with-tickets', label: 'Con boletas', count: counts.withTickets },
            { value: 'without-tickets', label: 'Sin boletas', count: counts.withoutTickets },
          ]}
        />
      </div>

      <Modal
        open={form.isOpen}
        onClose={closeForm}
        title={editing ? 'Editar participante' : 'Nuevo participante'}
        className="max-w-xl"
      >
        <ParticipantForm
          key={editing?.id ?? 'new'}
          participant={editing}
          onDone={closeForm}
          onCancel={closeForm}
        />
      </Modal>

      {isLoading && <Loader label="Cargando participantes…" />}
      {isError && (
        <Alert tone="danger" title="No pudimos cargar los participantes">
          {getApiErrorMessage(error, 'Intenta de nuevo más tarde.')}
        </Alert>
      )}
      {data && filtered.length === 0 ? (
        <EmptyState
          icon={<Users size={28} />}
          title="Sin participantes"
          description={
            search || statusFilter !== 'all'
              ? 'No hay resultados para tu búsqueda o filtro.'
              : 'Crea el primer participante.'
          }
        />
      ) : (
        data && (
          <ParticipantTable
            participants={filtered}
            deletingId={deleteParticipant.variables ?? null}
            deleteError={deleteParticipant.error}
            onEdit={openEdit}
            onDelete={(id) => deleteParticipant.mutate(id)}
          />
        )
      )}
    </>
  );
}
