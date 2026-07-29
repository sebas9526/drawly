'use client';

import { getApiErrorMessage, type RaffleDto } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Button } from '@drawly/ui/Button';
import { Checkbox } from '@drawly/ui/Checkbox';
import { Field } from '@drawly/ui/Field';
import { Input } from '@drawly/ui/Input';
import { Select } from '@drawly/ui/Select';
import { formatCurrency } from '@drawly/utils';
import { useEffect } from 'react';
import { Controller, useForm } from 'react-hook-form';

// Direct file import (not the feature barrel) — the collaborators barrel
// re-exports CollaboratorForm, which imports useRaffles from this feature's
// own barrel. Going through @/features/collaborators here would close that
// into a circular import between the two feature index files.
import {
  useCollaborators,
  useRaffleCollaborators,
  useSetRaffleCollaborators,
} from '@/features/collaborators/hooks/use-collaborators';

import { useCreateRaffle, useUpdateRaffle } from '../hooks/use-raffles';
import { createRaffleFormSchema, type CreateRaffleFormValues } from '../validators/raffle-form';

const EMPTY: CreateRaffleFormValues = {
  title: '',
  prize: '',
  description: '',
  ticket_price: '0',
  total_tickets: '100',
  starting_number: '1',
  draw_date: '',
  publish_at: '',
  collaborator_ids: [],
};

/** Converts an ISO timestamp into the `YYYY-MM-DDTHH:mm` shape `<input type="datetime-local">` expects. */
function toDatetimeLocal(iso: string): string {
  const date = new Date(iso);
  const pad = (n: number): string => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function toDefaults(raffle: RaffleDto | null | undefined): CreateRaffleFormValues {
  if (!raffle) return EMPTY;
  return {
    title: raffle.title,
    prize: raffle.prize,
    description: raffle.description,
    ticket_price: String(raffle.ticket_price),
    total_tickets: String(raffle.total_tickets),
    starting_number: String(raffle.starting_number),
    draw_date: toDatetimeLocal(raffle.draw_date),
    publish_at: raffle.publish_at ? toDatetimeLocal(raffle.publish_at) : '',
    collaborator_ids: [],
  };
}

interface RaffleFormProps {
  raffle?: RaffleDto | null;
  onDone?: () => void;
  /** Reports whether a create/update request is in flight, so a parent
   * rendering this inside a Modal can block it from being dismissed
   * mid-submit (see raffles-admin.tsx / dashboard-page.tsx). */
  onPendingChange?: (pending: boolean) => void;
}

export function RaffleForm({
  raffle,
  onDone,
  onPendingChange,
}: RaffleFormProps): React.JSX.Element {
  const { register, handleSubmit, control, setValue } = useForm<CreateRaffleFormValues>({
    defaultValues: toDefaults(raffle),
  });
  const { data: collaborators } = useCollaborators();
  const { data: currentCollaborators } = useRaffleCollaborators(raffle?.id ?? '');
  const create = useCreateRaffle();
  const update = useUpdateRaffle();
  const setRaffleCollaborators = useSetRaffleCollaborators();
  const pending = create.isPending || update.isPending || setRaffleCollaborators.isPending;
  const error = create.error ?? update.error ?? setRaffleCollaborators.error;

  useEffect(() => {
    onPendingChange?.(pending);
  }, [pending, onPendingChange]);

  // The raffle prop doesn't carry its collaborators inline (kept out of
  // RaffleRead so the raffles module stays unaware of collaborators) — seed
  // the checkboxes once the separate lookup resolves.
  useEffect(() => {
    if (currentCollaborators) {
      setValue(
        'collaborator_ids',
        currentCollaborators.map((collaborator) => collaborator.id),
      );
    }
  }, [currentCollaborators, setValue]);

  const onSubmit = handleSubmit((values) => {
    const parsed = createRaffleFormSchema.safeParse(values);
    if (!parsed.success) return;
    const { collaborator_ids } = parsed.data;

    if (raffle) {
      // starting_number is immutable once the raffle exists — never send it on update.
      const { title, description, prize, ticket_price, total_tickets, draw_date, publish_at } =
        parsed.data;
      update.mutate(
        {
          id: raffle.id,
          payload: {
            title,
            description,
            prize,
            ticket_price,
            total_tickets,
            draw_date,
            publish_at,
          },
        },
        {
          onSuccess: () => {
            setRaffleCollaborators.mutate(
              { raffleId: raffle.id, payload: { collaborator_ids } },
              { onSuccess: () => onDone?.() },
            );
          },
        },
      );
    } else {
      const {
        title,
        description,
        prize,
        ticket_price,
        total_tickets,
        starting_number,
        draw_date,
        publish_at,
      } = parsed.data;
      create.mutate(
        {
          title,
          description,
          prize,
          ticket_price,
          total_tickets,
          starting_number,
          draw_date,
          publish_at,
        },
        {
          onSuccess: (createdRaffle) => {
            if (collaborator_ids.length === 0) {
              onDone?.();
              return;
            }
            setRaffleCollaborators.mutate(
              { raffleId: createdRaffle.id, payload: { collaborator_ids } },
              { onSuccess: () => onDone?.() },
            );
          },
        },
      );
    }
  });

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <fieldset disabled={pending} className="m-0 min-w-0 border-0 p-0">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Título">
            <Input placeholder="Gran rifa 2026" {...register('title', { required: true })} />
          </Field>
          <Field label="Premio">
            <Input placeholder="Un carro 0km" {...register('prize', { required: true })} />
          </Field>
          <Field label="Precio por boleta">
            <Controller
              control={control}
              name="ticket_price"
              render={({ field }) => (
                <Input
                  inputMode="numeric"
                  placeholder="$ 0"
                  value={field.value ? formatCurrency(Number(field.value)) : ''}
                  onChange={(event) => field.onChange(event.target.value.replace(/\D/g, ''))}
                  onBlur={field.onBlur}
                />
              )}
            />
          </Field>
          <Field label="Total de boletas">
            <Input
              type="number"
              min={1}
              disabled={Boolean(raffle)}
              {...register('total_tickets')}
            />
          </Field>
          <Field label="Numeración inicial" hint="No se puede cambiar después de crear la rifa.">
            <Select disabled={Boolean(raffle)} {...register('starting_number')}>
              <option value="1">Empieza en 1 (ej. 001 - 100)</option>
              <option value="0">Empieza en 0 (ej. 00 - 99)</option>
            </Select>
          </Field>
          <Field label="Fecha del sorteo" htmlFor="draw_date">
            <Input
              id="draw_date"
              type="datetime-local"
              {...register('draw_date', { required: true })}
            />
          </Field>
          <Field
            label="Fecha de activación (opcional)"
            htmlFor="publish_at"
            hint="Si la defines, la rifa se publica sola ese día (necesita boletas ya generadas). Vacío = publicas tú manualmente."
          >
            <Input id="publish_at" type="datetime-local" {...register('publish_at')} />
          </Field>
        </div>

        <div className="mt-4">
          <Field
            label="Colaboradores"
            hint="Quiénes venden esta rifa. Puedes ajustarlo cuando quieras."
          >
            <Controller
              control={control}
              name="collaborator_ids"
              render={({ field }) =>
                (collaborators ?? []).length === 0 ? (
                  <p className="text-text-secondary text-sm">
                    Aún no tienes colaboradores creados.
                  </p>
                ) : (
                  <div className="border-border flex max-h-40 flex-col gap-2 overflow-y-auto rounded-lg border p-3">
                    {(collaborators ?? []).map((collaborator) => (
                      <Checkbox
                        key={collaborator.id}
                        label={collaborator.name}
                        checked={field.value.includes(collaborator.id)}
                        onChange={(event) => {
                          field.onChange(
                            event.target.checked
                              ? [...field.value, collaborator.id]
                              : field.value.filter((id) => id !== collaborator.id),
                          );
                        }}
                      />
                    ))}
                  </div>
                )
              }
            />
          </Field>
        </div>

        {error && (
          <Alert tone="danger" className="mt-4">
            {getApiErrorMessage(error, 'No se pudo guardar la rifa.')}
          </Alert>
        )}

        <div className="mt-4 flex justify-end">
          <Button type="submit" loading={pending}>
            {pending
              ? raffle
                ? 'Guardando...'
                : 'Creando...'
              : raffle
                ? 'Guardar cambios'
                : 'Crear rifa'}
          </Button>
        </div>
      </fieldset>
    </form>
  );
}
