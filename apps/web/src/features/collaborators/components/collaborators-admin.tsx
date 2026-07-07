'use client';

import { isApiError, type CollaboratorDto } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Button } from '@drawly/ui/Button';
import { EmptyState } from '@drawly/ui/EmptyState';
import { Loader } from '@drawly/ui/Loader';
import { Modal } from '@drawly/ui/Modal';
import { PageHeader } from '@drawly/ui/PageHeader';
import { SearchInput } from '@drawly/ui/SearchInput';
import { Select } from '@drawly/ui/Select';
import { useDisclosure } from '@drawly/ui/use-disclosure';
import { Plus, UserPlus } from 'lucide-react';
import { useMemo, useState } from 'react';

import { ROUTES } from '@drawly/constants';

import { useRaffles } from '@/features/raffles';

import {
  useCollaborators,
  useDeleteCollaborator,
  useSetCollaboratorActive,
} from '../hooks/use-collaborators';
import { CollaboratorForm } from './collaborator-form';
import { CollaboratorLeaderboard } from './collaborator-leaderboard';
import { CollaboratorTable } from './collaborator-table';

export function CollaboratorsAdmin(): React.JSX.Element {
  const [search, setSearch] = useState('');
  const [raffleId, setRaffleId] = useState('');
  const [editing, setEditing] = useState<CollaboratorDto | null>(null);
  const form = useDisclosure();

  const { data: raffles } = useRaffles();
  const { data, isLoading, isError, error } = useCollaborators({
    raffleId: raffleId || undefined,
    search: search.trim() || undefined,
  });
  const deleteCollaborator = useDeleteCollaborator();
  const setActive = useSetCollaboratorActive();

  const raffleNameById = useMemo(() => {
    const map = new Map((raffles?.data ?? []).map((r) => [r.id, r.title]));
    return (id: string): string => map.get(id) ?? '—';
  }, [raffles]);

  const raffleSlugById = useMemo(() => {
    const map = new Map((raffles?.data ?? []).map((r) => [r.id, r.public_slug]));
    return (id: string): string | undefined => map.get(id);
  }, [raffles]);

  const copyReferralLink = async (collaborator: CollaboratorDto): Promise<boolean> => {
    const slug = raffleSlugById(collaborator.raffle_id);
    if (!slug) return false;
    const url = `${window.location.origin}${ROUTES.PUBLIC_RAFFLE(slug)}?ref=${collaborator.id}`;
    await navigator.clipboard.writeText(url);
    return true;
  };

  const selectedRaffle = useMemo(
    () => (raffles?.data ?? []).find((r) => r.id === raffleId) ?? null,
    [raffles, raffleId],
  );

  const openCreate = (): void => {
    setEditing(null);
    form.open();
  };
  const openEdit = (collaborator: CollaboratorDto): void => {
    setEditing(collaborator);
    form.open();
  };
  const closeForm = (): void => {
    form.close();
    setEditing(null);
  };

  const hasRaffles = (raffles?.data ?? []).length > 0;

  return (
    <>
      <PageHeader
        title="Colaboradores"
        description="Administra tu equipo de venta de boletas por rifa."
        actions={
          <Button leftIcon={<Plus size={16} />} onClick={openCreate} disabled={!hasRaffles}>
            Nuevo colaborador
          </Button>
        }
      />

      <div className="flex flex-col gap-3 sm:flex-row">
        <SearchInput
          containerClassName="max-w-md flex-1"
          placeholder="Buscar por nombre, teléfono o correo"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <Select
          className="sm:max-w-xs"
          value={raffleId}
          onChange={(event) => setRaffleId(event.target.value)}
          aria-label="Filtrar por rifa"
        >
          <option value="">Todas las rifas</option>
          {(raffles?.data ?? []).map((raffle) => (
            <option key={raffle.id} value={raffle.id}>
              {raffle.title}
            </option>
          ))}
        </Select>
      </div>

      {hasRaffles && (
        <div className="flex flex-col gap-3">
          <h2 className="text-text-primary text-sm font-semibold">Ranking de ventas</h2>
          {selectedRaffle ? (
            <CollaboratorLeaderboard
              raffleId={selectedRaffle.id}
              raffleTotalTickets={selectedRaffle.total_tickets}
            />
          ) : (
            <Alert tone="info">Selecciona una rifa para ver el ranking de colaboradores.</Alert>
          )}
        </div>
      )}

      <Modal
        open={form.isOpen}
        onClose={closeForm}
        title={editing ? 'Editar colaborador' : 'Nuevo colaborador'}
        className="max-w-xl"
      >
        <CollaboratorForm
          key={editing?.id ?? 'new'}
          collaborator={editing}
          defaultRaffleId={raffleId}
          onDone={closeForm}
          onCancel={closeForm}
        />
      </Modal>

      {!hasRaffles && (
        <Alert tone="info" title="Primero crea una rifa">
          Los colaboradores pertenecen a una rifa. Crea una rifa para empezar a añadir tu equipo de
          ventas.
        </Alert>
      )}

      {isLoading && <Loader label="Cargando colaboradores…" />}
      {isError && (
        <Alert tone="danger" title="No pudimos cargar los colaboradores">
          {isApiError(error) ? error.message : 'Intenta de nuevo más tarde.'}
        </Alert>
      )}
      {data && data.data.length === 0
        ? hasRaffles && (
            <EmptyState
              icon={<UserPlus size={28} />}
              title="Sin colaboradores"
              description={
                search || raffleId
                  ? 'No hay resultados para tu búsqueda.'
                  : 'Crea el primer colaborador de venta.'
              }
            />
          )
        : data && (
            <CollaboratorTable
              collaborators={data.data}
              raffleNameById={raffleNameById}
              deletingId={deleteCollaborator.variables ?? null}
              deleteError={deleteCollaborator.error}
              onEdit={openEdit}
              onToggleActive={(c) => setActive.mutate({ id: c.id, isActive: !c.is_active })}
              onDelete={(id) => deleteCollaborator.mutate(id)}
              onCopyLink={copyReferralLink}
            />
          )}
    </>
  );
}
