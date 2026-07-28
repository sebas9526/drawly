/** Shared semantic tones for Badge / StatusBadge / StatCard / ProgressBar.
 * Token-based so they adapt to light and dark automatically. Domain code maps
 * its statuses to a Tone to keep these components generic.
 *
 * `prize` is reserved for winner/prize/podium/draw-result moments — never
 * reuse `warning` for those, they read as "caution", not "you won". */
export type Tone = 'neutral' | 'primary' | 'success' | 'warning' | 'info' | 'danger' | 'prize';

export const TONE_SOFT: Record<Tone, string> = {
  neutral: 'bg-muted text-text-secondary',
  primary: 'bg-primary/10 text-primary',
  success: 'bg-success/10 text-success',
  warning: 'bg-warning/10 text-warning',
  info: 'bg-info/10 text-info',
  danger: 'bg-danger/10 text-danger',
  prize: 'bg-prize/10 text-prize',
};

export const TONE_DOT: Record<Tone, string> = {
  neutral: 'bg-text-muted',
  primary: 'bg-primary',
  success: 'bg-success',
  warning: 'bg-warning',
  info: 'bg-info',
  danger: 'bg-danger',
  prize: 'bg-prize',
};

/** Solid (filled) tone — always paired with `-fg`, which is guaranteed
 * legible against `-solid` in both themes (see globals.css: `*-solid` picks
 * a fixed, sufficiently dark shade rather than the theme-swapping `*`
 * token, specifically so text can safely sit on top of it). */
export const TONE_SOLID: Record<Tone, string> = {
  neutral: 'bg-text-secondary text-surface',
  primary: 'bg-primary text-primary-fg',
  success: 'bg-success-solid text-success-fg',
  warning: 'bg-warning-solid text-warning-fg',
  info: 'bg-info-solid text-info-fg',
  danger: 'bg-danger-solid text-danger-fg',
  prize: 'bg-prize-solid text-prize-fg',
};

/** Paintable (non-Tailwind-class) colors for charts — SVG `stroke`/`fill` and
 * inline `style` can't consume utility classes, so these resolve straight to
 * the same CSS custom properties the classes above use, keeping charts on the
 * same tokens (and automatic light/dark) as every other tone-driven component. */
export const TONE_CHART_COLOR: Record<Tone, string> = {
  neutral: 'rgb(var(--color-text-muted))',
  primary: 'rgb(var(--color-primary))',
  success: 'rgb(var(--color-success))',
  warning: 'rgb(var(--color-warning))',
  info: 'rgb(var(--color-info))',
  danger: 'rgb(var(--color-danger))',
  prize: 'rgb(var(--color-prize))',
};
