'use client';

import { getApiErrorMessage, type CollaboratorDto } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Button } from '@drawly/ui/Button';
import { Checkbox } from '@drawly/ui/Checkbox';
import { Field } from '@drawly/ui/Field';
import { Input } from '@drawly/ui/Input';
import { Switch } from '@drawly/ui/Switch';
import { Textarea } from '@drawly/ui/Textarea';
import { Check } from 'lucide-react';
import { Controller, useForm } from 'react-hook-form';

import { useRaffles } from '@/features/raffles';

import { useCreateCollaborator, useUpdateCollaborator } from '../hooks/use-collaborators';
import {
  COLLABORATOR_COLORS,
  collaboratorFormSchema,
  type CollaboratorFormValues,
} from '../validators/collaborator-form';

interface CollaboratorFormProps {
  collaborator?: CollaboratorDto | null;
  defaultRaffleId?: string;
  onDone: () => void;
  onCancel: () => void;
}

function toDefaults(
  collaborator: CollaboratorDto | null | undefined,
  defaultRaffleId: string,
): CollaboratorFormValues {
  return {
    raffle_ids: collaborator?.raffle_ids ?? (defaultRaffleId ? [defaultRaffleId] : []),
    name: collaborator?.name ?? '',
    phone: collaborator?.phone ?? '',
    email: collaborator?.email ?? '',
    color: collaborator?.color ?? COLLABORATOR_COLORS[0],
    notes: collaborator?.notes ?? '',
    is_active: collaborator?.is_active ?? true,
  };
}

export function CollaboratorForm({
  collaborator,
  defaultRaffleId = '',
  onDone,
  onCancel,
}: CollaboratorFormProps): React.JSX.Element {
  const isEditing = collaborator != null;
  const { data: raffles } = useRaffles();
  const create = useCreateCollaborator();
  const update = useUpdateCollaborator();

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<CollaboratorFormValues>({
    defaultValues: toDefaults(collaborator, defaultRaffleId),
  });

  const pending = create.isPending || update.isPending;
  const mutationError = create.error ?? update.error;

  const onSubmit = handleSubmit((values) => {
    const parsed = collaboratorFormSchema.safeParse(values);
    if (!parsed.success) return;
    const { raffle_ids, name, phone, email, color, notes, is_active } = parsed.data;

    if (isEditing) {
      update.mutate(
        {
          id: collaborator.id,
          payload: {
            raffle_ids,
            name,
            phone: phone || undefined,
            email: email || undefined,
            color,
            notes: notes || undefined,
            is_active,
          },
        },
        { onSuccess: onDone },
      );
      return;
    }

    create.mutate(
      {
        raffle_ids,
        name,
        phone: phone || undefined,
        email: email || undefined,
        color,
        notes: notes || undefined,
        is_active,
      },
      { onSuccess: onDone },
    );
  });

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
      <Field label="Rifas" error={errors.raffle_ids?.message}>
        <Controller
          control={control}
          name="raffle_ids"
          render={({ field }) => (
            <div className="border-border flex max-h-40 flex-col gap-2 overflow-y-auto rounded-lg border p-3">
              {(raffles ?? []).map((raffle) => (
                <Checkbox
                  key={raffle.id}
                  label={raffle.title}
                  checked={field.value.includes(raffle.id)}
                  onChange={(event) => {
                    field.onChange(
                      event.target.checked
                        ? [...field.value, raffle.id]
                        : field.value.filter((id) => id !== raffle.id),
                    );
                  }}
                />
              ))}
            </div>
          )}
        />
      </Field>

      <Field label="Nombre" htmlFor="name" error={errors.name?.message}>
        <Input id="name" placeholder="Juan Pérez" {...register('name')} />
      </Field>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Teléfono" htmlFor="phone" error={errors.phone?.message}>
          <Input id="phone" placeholder="3001234567" {...register('phone')} />
        </Field>
        <Field label="Correo" htmlFor="email" error={errors.email?.message}>
          <Input id="email" type="email" placeholder="juan@ejemplo.com" {...register('email')} />
        </Field>
      </div>

      <Field label="Color" error={errors.color?.message}>
        <Controller
          control={control}
          name="color"
          render={({ field }) => (
            <div className="flex flex-wrap gap-2">
              {COLLABORATOR_COLORS.map((color) => (
                <button
                  key={color}
                  type="button"
                  aria-label={`Color ${color}`}
                  onClick={() => field.onChange(color)}
                  className="ring-offset-surface flex h-8 w-8 items-center justify-center rounded-full ring-2 ring-offset-2 transition"
                  style={{
                    backgroundColor: color,
                    // Highlight the selected swatch.
                    boxShadow: field.value === color ? `0 0 0 2px ${color}` : undefined,
                  }}
                >
                  {field.value === color && <Check size={16} className="text-white" />}
                </button>
              ))}
            </div>
          )}
        />
      </Field>

      <Field label="Notas" htmlFor="notes" error={errors.notes?.message}>
        <Textarea
          id="notes"
          rows={2}
          placeholder="Notas internas (opcional)"
          {...register('notes')}
        />
      </Field>

      <Controller
        control={control}
        name="is_active"
        render={({ field }) => (
          <div className="flex items-center justify-between">
            <span className="text-text-primary text-sm font-medium">Activo</span>
            <Switch
              checked={field.value}
              onCheckedChange={field.onChange}
              aria-label="Colaborador activo"
            />
          </div>
        )}
      />

      {mutationError != null && (
        <Alert tone="danger">
          {getApiErrorMessage(mutationError, 'No se pudo guardar el colaborador.')}
        </Alert>
      )}

      <div className="flex justify-end gap-2">
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" loading={pending}>
          {isEditing ? 'Guardar cambios' : 'Crear colaborador'}
        </Button>
      </div>
    </form>
  );
}
