'use client';

import type { PublicCollaboratorView } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Button } from '@drawly/ui/Button';
import { Field } from '@drawly/ui/Field';
import { Input } from '@drawly/ui/Input';
import { Select } from '@drawly/ui/Select';
import { formatTicketNumber } from '@drawly/utils';
import { useState } from 'react';
import { useForm } from 'react-hook-form';

import {
  EMPTY_RESERVE_FORM,
  reserveFormSchema,
  type ReserveFormValues,
} from '../validators/reserve-form';

interface ReserveFormProps {
  ticketNumber: number;
  /** Largest generated ticket number (starting_number + total_tickets - 1) —
   * drives zero-padding width. */
  maxNumber: number;
  pending: boolean;
  errorMessage: string | null;
  collaborators: PublicCollaboratorView[];
  /** Set when the reservation link carries a `?ref=<collaboratorId>` token —
   * the field is then shown as a locked badge instead of an editable select,
   * so referral attribution can't be mistyped or swapped. */
  lockedCollaborator?: PublicCollaboratorView | null;
  onSubmit: (values: ReserveFormValues) => void;
  onCancel: () => void;
}

export function ReserveForm({
  ticketNumber,
  maxNumber,
  pending,
  errorMessage,
  collaborators,
  lockedCollaborator,
  onSubmit,
  onCancel,
}: ReserveFormProps): React.JSX.Element {
  const { register, handleSubmit } = useForm<ReserveFormValues>({
    defaultValues: { ...EMPTY_RESERVE_FORM, collaborator_id: lockedCollaborator?.id ?? '' },
  });
  const [validationError, setValidationError] = useState<string | null>(null);

  const noCollaboratorsAvailable = !lockedCollaborator && collaborators.length === 0;

  const submit = handleSubmit((values) => {
    const finalValues = lockedCollaborator
      ? { ...values, collaborator_id: lockedCollaborator.id }
      : values;
    const result = reserveFormSchema.safeParse(finalValues);
    if (!result.success) {
      setValidationError(result.error.issues[0]?.message ?? 'Revisa los datos del formulario.');
      return;
    }
    setValidationError(null);
    onSubmit(finalValues);
  });

  return (
    <form onSubmit={submit} className="flex flex-col gap-4">
      <div className="bg-primary/5 border-primary/20 flex items-center gap-2 rounded-lg border p-3 text-sm">
        <span className="text-text-secondary">Reservando la boleta</span>
        <span className="text-primary font-mono text-base font-semibold">
          #{formatTicketNumber(ticketNumber, maxNumber)}
        </span>
      </div>

      <Field label="Nombre completo">
        <Input placeholder="Tu nombre" {...register('full_name')} />
      </Field>
      <Field label="Teléfono">
        <Input placeholder="300 123 4567" {...register('phone')} />
      </Field>
      <Field label="Correo (opcional)">
        <Input type="email" {...register('email')} />
      </Field>
      <Field label="Documento (opcional)">
        <Input {...register('document')} />
      </Field>

      {lockedCollaborator ? (
        <Field label="Vendido por">
          <div className="border-border bg-muted/40 flex items-center gap-2 rounded-lg border px-3 py-2.5 text-sm">
            <span
              className="h-2.5 w-2.5 shrink-0 rounded-full"
              style={{ backgroundColor: lockedCollaborator.color }}
              aria-hidden
            />
            <span className="text-text-primary font-medium">{lockedCollaborator.name}</span>
          </div>
        </Field>
      ) : noCollaboratorsAvailable ? (
        <Alert tone="info">
          Esta rifa aún no tiene vendedores configurados. Contacta al organizador para reservar una
          boleta.
        </Alert>
      ) : (
        <Field label="Vendido por">
          <Select {...register('collaborator_id')}>
            <option value="">Selecciona un vendedor</option>
            {collaborators.map((collaborator) => (
              <option key={collaborator.id} value={collaborator.id}>
                {collaborator.name}
              </option>
            ))}
          </Select>
        </Field>
      )}

      {(validationError ?? errorMessage) && (
        <Alert tone="danger">{validationError ?? errorMessage}</Alert>
      )}

      <div className="flex gap-2">
        <Button
          type="submit"
          className="flex-1"
          loading={pending}
          disabled={noCollaboratorsAvailable}
        >
          Confirmar reserva
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          Elegir otra
        </Button>
      </div>
    </form>
  );
}
