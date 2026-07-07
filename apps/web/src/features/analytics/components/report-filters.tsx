'use client';

import { Field } from '@drawly/ui/Field';
import { Input } from '@drawly/ui/Input';
import { Select } from '@drawly/ui/Select';

import { useRaffleCollaborators } from '@/features/collaborators';
import { useRaffles } from '@/features/raffles';

import type { ReportFilterValues } from '../validators/report-filters';

export type ReportFilterField = 'dateRange' | 'raffle' | 'raffleStatus' | 'status' | 'collaborator';

interface ReportFiltersProps {
  fields: ReportFilterField[];
  value: ReportFilterValues;
  onChange: (value: ReportFilterValues) => void;
}

/** Shared filter row for every report page — which fields render is
 * per-page (`fields`), so pages don't repeat the same filter markup. */
export function ReportFilters({ fields, value, onChange }: ReportFiltersProps): React.JSX.Element {
  const { data: raffles } = useRaffles();
  const { data: collaborators } = useRaffleCollaborators(value.raffleId);

  const set = <K extends keyof ReportFilterValues>(key: K, next: ReportFilterValues[K]): void => {
    onChange({ ...value, [key]: next });
  };

  return (
    <div className="flex flex-wrap items-end gap-3">
      {fields.includes('dateRange') && (
        <>
          <Field label="Desde">
            <Input
              type="date"
              className="w-40"
              value={value.startDate}
              onChange={(event) => set('startDate', event.target.value)}
            />
          </Field>
          <Field label="Hasta">
            <Input
              type="date"
              className="w-40"
              value={value.endDate}
              onChange={(event) => set('endDate', event.target.value)}
            />
          </Field>
        </>
      )}

      {fields.includes('raffle') && (
        <Field label="Rifa">
          <Select
            className="w-48"
            value={value.raffleId}
            onChange={(event) => set('raffleId', event.target.value)}
          >
            <option value="">Todas</option>
            {(raffles?.data ?? []).map((raffle) => (
              <option key={raffle.id} value={raffle.id}>
                {raffle.title}
              </option>
            ))}
          </Select>
        </Field>
      )}

      {fields.includes('raffleStatus') && (
        <Field label="Estado de rifa">
          <Select
            className="w-40"
            value={value.raffleStatus}
            onChange={(event) => set('raffleStatus', event.target.value)}
          >
            <option value="">Todos</option>
            <option value="draft">Borrador</option>
            <option value="published">Publicada</option>
            <option value="closed">Finalizada</option>
            <option value="archived">Archivada</option>
          </Select>
        </Field>
      )}

      {fields.includes('status') && (
        <Field label="Estado de boleta">
          <Select
            className="w-40"
            value={value.status}
            onChange={(event) => set('status', event.target.value)}
          >
            <option value="">Todos</option>
            <option value="available">Disponible</option>
            <option value="reserved">Reservada</option>
            <option value="paid">Pagada</option>
          </Select>
        </Field>
      )}

      {fields.includes('collaborator') && (
        <Field label="Colaborador">
          <Select
            className="w-48"
            value={value.collaboratorId}
            onChange={(event) => set('collaboratorId', event.target.value)}
            disabled={!value.raffleId}
          >
            <option value="">{value.raffleId ? 'Todos' : 'Selecciona una rifa'}</option>
            {(collaborators ?? []).map((collaborator) => (
              <option key={collaborator.id} value={collaborator.id}>
                {collaborator.name}
              </option>
            ))}
          </Select>
        </Field>
      )}
    </div>
  );
}
