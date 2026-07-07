export { formatCurrency } from '@drawly/utils';
export { RAFFLE_STATUS_PRESENTATION } from '@/features/raffles/services/raffle-status';

const dateTime = new Intl.DateTimeFormat('es-CO', { dateStyle: 'short', timeStyle: 'short' });

export function formatDateTime(iso: string): string {
  return dateTime.format(new Date(iso));
}
