const drawDateFormatter = new Intl.DateTimeFormat('es-CO', { dateStyle: 'medium' });

export function formatDrawDate(iso: string): string {
  return drawDateFormatter.format(new Date(iso));
}
