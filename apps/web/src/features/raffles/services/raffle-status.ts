import type { RaffleStatus } from '@drawly/api-client';
import type { Tone } from '@drawly/ui/tones';

/** Presentation-only mapping of a raffle status to a label + UI tone. Canonical
 * source — other features (dashboard) import this instead of redefining it. */
export const RAFFLE_STATUS_PRESENTATION: Record<RaffleStatus, { label: string; tone: Tone }> = {
  draft: { label: 'Borrador', tone: 'neutral' },
  published: { label: 'Publicada', tone: 'success' },
  closed: { label: 'Finalizada', tone: 'info' },
  archived: { label: 'Archivada', tone: 'neutral' },
};
