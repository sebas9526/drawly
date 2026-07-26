'use client';

import { getApiErrorMessage, type ParticipantDto } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Button } from '@drawly/ui/Button';
import { Field } from '@drawly/ui/Field';
import { Input } from '@drawly/ui/Input';
import { Textarea } from '@drawly/ui/Textarea';
import { useForm } from 'react-hook-form';

import { useCreateParticipant, useUpdateParticipant } from '../hooks/use-participants';
import {
  EMPTY_PARTICIPANT_FORM,
  participantFormSchema,
  type ParticipantFormValues,
} from '../validators/participant-form';

interface ParticipantFormProps {
  participant?: ParticipantDto | null;
  onDone: () => void;
  onCancel: () => void;
}

function toDefaults(participant: ParticipantDto | null | undefined): ParticipantFormValues {
  if (!participant) return EMPTY_PARTICIPANT_FORM;
  return {
    full_name: participant.full_name,
    phone: participant.phone,
    email: participant.email ?? '',
    document: participant.document ?? '',
    city: participant.city ?? '',
    address: participant.address ?? '',
    notes: participant.notes ?? '',
  };
}

function toPayload(values: ParticipantFormValues) {
  return {
    full_name: values.full_name.trim(),
    phone: values.phone.trim(),
    email: values.email.trim() || undefined,
    document: values.document.trim() || undefined,
    city: values.city.trim() || undefined,
    address: values.address.trim() || undefined,
    notes: values.notes.trim() || undefined,
  };
}

export function ParticipantForm({
  participant,
  onDone,
  onCancel,
}: ParticipantFormProps): React.JSX.Element {
  const { register, handleSubmit } = useForm<ParticipantFormValues>({
    defaultValues: toDefaults(participant),
  });
  const create = useCreateParticipant();
  const update = useUpdateParticipant();
  const pending = create.isPending || update.isPending;
  const error = create.error ?? update.error;

  const onSubmit = handleSubmit((values) => {
    if (!participantFormSchema.safeParse(values).success) return;
    const payload = toPayload(values);
    if (participant) {
      update.mutate({ id: participant.id, payload }, { onSuccess: onDone });
    } else {
      create.mutate(payload, { onSuccess: onDone });
    }
  });

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Nombre completo">
          <Input placeholder="Ana Díaz" {...register('full_name')} />
        </Field>
        <Field label="Teléfono">
          <Input placeholder="3001234567" {...register('phone')} />
        </Field>
        <Field label="Correo">
          <Input type="email" placeholder="ana@correo.com" {...register('email')} />
        </Field>
        <Field label="Documento">
          <Input placeholder="CC 123456" {...register('document')} />
        </Field>
        <Field label="Ciudad">
          <Input {...register('city')} />
        </Field>
        <Field label="Dirección">
          <Input {...register('address')} />
        </Field>
      </div>
      <Field label="Notas">
        <Textarea rows={2} {...register('notes')} />
      </Field>

      {error && (
        <Alert tone="danger">
          {getApiErrorMessage(error, 'No se pudo guardar el participante.')}
        </Alert>
      )}

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" loading={pending}>
          {participant ? 'Guardar cambios' : 'Crear participante'}
        </Button>
      </div>
    </form>
  );
}
