'use client';

import { isApiError, type RaffleDto } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Button } from '@drawly/ui/Button';
import { ConfirmDialog } from '@drawly/ui/ConfirmDialog';
import { EmptyState } from '@drawly/ui/EmptyState';
import { LoadingCard } from '@drawly/ui/LoadingCard';
import { Modal } from '@drawly/ui/Modal';
import { PageHeader } from '@drawly/ui/PageHeader';
import { SearchInput } from '@drawly/ui/SearchInput';
import { useDisclosure } from '@drawly/ui/use-disclosure';
import { Plus, Sparkles } from 'lucide-react';
import { useEffect, useState } from 'react';

import { useDeleteRaffle, useRaffles } from '../hooks/use-raffles';
import { RaffleCard } from './raffle-card';
import { RaffleForm } from './raffle-form';

export function RafflesAdmin(): React.JSX.Element {
  const [search, setSearch] = useState('');
  const [editing, setEditing] = useState<RaffleDto | null>(null);
  const [deleting, setDeleting] = useState<RaffleDto | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const form = useDisclosure();

  const { data, isLoading, isError, error } = useRaffles({ search: search.trim() || undefined });
  const deleteRaffle = useDeleteRaffle();

  useEffect(() => {
    if (!notice) return;
    const timeout = setTimeout(() => setNotice(null), 4000);
    return () => clearTimeout(timeout);
  }, [notice]);

  const openCreate = (): void => {
    setEditing(null);
    form.open();
  };
  const openEdit = (raffle: RaffleDto): void => {
    setEditing(raffle);
    form.open();
  };
  const closeForm = (): void => {
    form.close();
    setEditing(null);
  };

  return (
    <>
      <PageHeader
        title="Rifas"
        description="Crea, genera boletas y publica tus rifas."
        actions={
          <Button leftIcon={<Plus size={16} />} onClick={openCreate}>
            Nueva rifa
          </Button>
        }
      />

      <SearchInput
        containerClassName="max-w-md"
        placeholder="Buscar por título o premio"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
      />

      {notice && <Alert tone="info" title={notice} className="animate-fade-in-up" />}

      <Modal
        open={form.isOpen}
        onClose={closeForm}
        title={editing ? 'Editar rifa' : 'Nueva rifa'}
        className="max-w-xl"
      >
        <RaffleForm key={editing?.id ?? 'new'} raffle={editing} onDone={closeForm} />
      </Modal>

      <ConfirmDialog
        open={deleting !== null}
        onClose={() => setDeleting(null)}
        onConfirm={() => {
          if (deleting) deleteRaffle.mutate(deleting.id);
          setDeleting(null);
        }}
        title="Eliminar rifa"
        description={
          deleting
            ? `¿Seguro que quieres eliminar "${deleting.title}"? Esta acción no se puede deshacer.`
            : undefined
        }
        confirmLabel="Eliminar"
        tone="danger"
      />

      {deleteRaffle.isError && (
        <Alert tone="danger">
          {isApiError(deleteRaffle.error)
            ? deleteRaffle.error.message
            : 'No se pudo eliminar la rifa.'}
        </Alert>
      )}

      {isLoading && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <LoadingCard key={index} lines={3} />
          ))}
        </div>
      )}
      {isError && (
        <Alert tone="danger" title="No pudimos cargar las rifas">
          {isApiError(error) ? error.message : 'Intenta de nuevo más tarde.'}
        </Alert>
      )}
      {data && data.data.length === 0 && (
        <EmptyState
          icon={<Sparkles size={28} />}
          title={search ? 'Sin resultados' : 'Aún no hay rifas'}
          description={
            search
              ? 'No hay rifas que coincidan con tu búsqueda.'
              : 'Crea tu primera rifa para empezar a vender boletas.'
          }
          action={
            !search && (
              <Button leftIcon={<Plus size={16} />} onClick={openCreate}>
                Nueva rifa
              </Button>
            )
          }
        />
      )}
      {data && data.data.length > 0 && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {data.data.map((raffle) => (
            <RaffleCard
              key={raffle.id}
              raffle={raffle}
              onEdit={openEdit}
              onDelete={setDeleting}
              onDuplicate={() => setNotice('Duplicar rifas estará disponible próximamente.')}
            />
          ))}
        </div>
      )}
    </>
  );
}
