'use client';

import { isApiError, type RaffleDto } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Button } from '@drawly/ui/Button';
import { Field } from '@drawly/ui/Field';
import { Input } from '@drawly/ui/Input';
import { useForm } from 'react-hook-form';

import { useCreateRaffle, useUpdateRaffle } from '../hooks/use-raffles';
import { createRaffleFormSchema, type CreateRaffleFormValues } from '../validators/raffle-form';

const EMPTY: CreateRaffleFormValues = {
  title: '',
  prize: '',
  description: '',
  ticket_price: '0',
  total_tickets: '100',
  draw_date: '',
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
    draw_date: toDatetimeLocal(raffle.draw_date),
  };
}

interface RaffleFormProps {
  raffle?: RaffleDto | null;
  onDone?: () => void;
}

export function RaffleForm({ raffle, onDone }: RaffleFormProps): React.JSX.Element {
  const { register, handleSubmit } = useForm<CreateRaffleFormValues>({
    defaultValues: toDefaults(raffle),
  });
  const create = useCreateRaffle();
  const update = useUpdateRaffle();
  const pending = create.isPending || update.isPending;
  const error = create.error ?? update.error;

  const onSubmit = handleSubmit((values) => {
    const parsed = createRaffleFormSchema.safeParse(values);
    if (!parsed.success) return;
    if (raffle) {
      update.mutate({ id: raffle.id, payload: parsed.data }, { onSuccess: () => onDone?.() });
    } else {
      create.mutate(parsed.data, { onSuccess: () => onDone?.() });
    }
  });

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Título">
          <Input placeholder="Gran rifa 2026" {...register('title', { required: true })} />
        </Field>
        <Field label="Premio">
          <Input placeholder="Un carro 0km" {...register('prize', { required: true })} />
        </Field>
        <Field label="Precio por boleta">
          <Input type="number" min={0} {...register('ticket_price')} />
        </Field>
        <Field label="Total de boletas">
          <Input type="number" min={1} disabled={Boolean(raffle)} {...register('total_tickets')} />
        </Field>
        <Field label="Fecha del sorteo" htmlFor="draw_date">
          <Input
            id="draw_date"
            type="datetime-local"
            {...register('draw_date', { required: true })}
          />
        </Field>
      </div>

      {error && (
        <Alert tone="danger">
          {isApiError(error) ? error.message : 'No se pudo guardar la rifa.'}
        </Alert>
      )}

      <div className="flex justify-end">
        <Button type="submit" loading={pending}>
          {raffle ? 'Guardar cambios' : 'Crear rifa'}
        </Button>
      </div>
    </form>
  );
}
