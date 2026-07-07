/** Shared semantic tones for Badge / StatusBadge / StatCard. Token-based so they
 * adapt to light and dark automatically. Domain code maps its statuses to a Tone
 * to keep these components generic. */
export type Tone = 'neutral' | 'primary' | 'success' | 'warning' | 'info' | 'danger';

export const TONE_SOFT: Record<Tone, string> = {
  neutral: 'bg-muted text-text-secondary',
  primary: 'bg-primary/10 text-primary',
  success: 'bg-success/10 text-success',
  warning: 'bg-warning/10 text-warning',
  info: 'bg-info/10 text-info',
  danger: 'bg-danger/10 text-danger',
};

export const TONE_DOT: Record<Tone, string> = {
  neutral: 'bg-text-muted',
  primary: 'bg-primary',
  success: 'bg-success',
  warning: 'bg-warning',
  info: 'bg-info',
  danger: 'bg-danger',
};

export const TONE_SOLID: Record<Tone, string> = {
  neutral: 'bg-text-secondary text-surface',
  primary: 'bg-primary text-primary-fg',
  success: 'bg-success text-white',
  warning: 'bg-warning text-white',
  info: 'bg-info text-white',
  danger: 'bg-danger text-white',
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
};
