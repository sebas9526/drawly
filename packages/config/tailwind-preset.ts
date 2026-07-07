import type { Config } from 'tailwindcss';

/**
 * Shared Tailwind preset carrying the Drawly design tokens
 * (see docs/05-design-system/COLORS.md and DESIGN_SYSTEM.md).
 *
 * Colors reference CSS variables so light/dark themes swap without duplicating
 * the palette. Full 50–900 palette scales are exposed alongside semantic tokens
 * (background/surface/card/border/text/primary/…). Components consume these
 * tokens only — no hardcoded colors, sizes, radii, or shadows.
 */
const scale = (name: string) => ({
  50: `rgb(var(--${name}-50) / <alpha-value>)`,
  100: `rgb(var(--${name}-100) / <alpha-value>)`,
  200: `rgb(var(--${name}-200) / <alpha-value>)`,
  300: `rgb(var(--${name}-300) / <alpha-value>)`,
  400: `rgb(var(--${name}-400) / <alpha-value>)`,
  500: `rgb(var(--${name}-500) / <alpha-value>)`,
  600: `rgb(var(--${name}-600) / <alpha-value>)`,
  700: `rgb(var(--${name}-700) / <alpha-value>)`,
  800: `rgb(var(--${name}-800) / <alpha-value>)`,
  900: `rgb(var(--${name}-900) / <alpha-value>)`,
});

const preset: Omit<Config, 'content'> = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Palette scales
        indigo: scale('primary'),
        neutral: {
          ...scale('neutral'),
          950: 'rgb(var(--neutral-950) / <alpha-value>)',
        },
        // Semantic — primary + states (with subtle scale shades where useful)
        primary: {
          ...scale('primary'),
          DEFAULT: 'rgb(var(--color-primary) / <alpha-value>)',
          hover: 'rgb(var(--color-primary-hover) / <alpha-value>)',
          fg: 'rgb(var(--color-primary-fg) / <alpha-value>)',
        },
        secondary: 'rgb(var(--color-secondary) / <alpha-value>)',
        success: {
          DEFAULT: 'rgb(var(--color-success) / <alpha-value>)',
          soft: 'rgb(var(--success-100) / <alpha-value>)',
        },
        warning: {
          DEFAULT: 'rgb(var(--color-warning) / <alpha-value>)',
          soft: 'rgb(var(--warning-100) / <alpha-value>)',
        },
        danger: {
          DEFAULT: 'rgb(var(--color-danger) / <alpha-value>)',
          soft: 'rgb(var(--danger-100) / <alpha-value>)',
        },
        info: {
          DEFAULT: 'rgb(var(--color-info) / <alpha-value>)',
          soft: 'rgb(var(--info-100) / <alpha-value>)',
        },
        // Surfaces & text
        background: 'rgb(var(--color-background) / <alpha-value>)',
        surface: 'rgb(var(--color-surface) / <alpha-value>)',
        card: 'rgb(var(--color-card) / <alpha-value>)',
        muted: 'rgb(var(--color-muted) / <alpha-value>)',
        border: 'rgb(var(--color-border) / <alpha-value>)',
        'border-strong': 'rgb(var(--color-border-strong) / <alpha-value>)',
        ring: 'rgb(var(--color-ring) / <alpha-value>)',
        'text-primary': 'rgb(var(--color-text-primary) / <alpha-value>)',
        'text-secondary': 'rgb(var(--color-text-secondary) / <alpha-value>)',
        'text-muted': 'rgb(var(--color-text-muted) / <alpha-value>)',
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        xs: '0.25rem',
        sm: '0.375rem',
        md: '0.5rem',
        lg: '0.75rem',
        xl: '1rem',
        '2xl': '1.25rem',
        DEFAULT: 'var(--radius)',
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgb(15 23 42 / 0.06)',
        md: '0 4px 12px -2px rgb(15 23 42 / 0.08)',
        lg: '0 12px 28px -6px rgb(15 23 42 / 0.12)',
        xl: '0 24px 48px -12px rgb(15 23 42 / 0.18)',
      },
      transitionDuration: {
        DEFAULT: '150ms',
      },
      keyframes: {
        'fade-in': { from: { opacity: '0' }, to: { opacity: '1' } },
        'fade-in-up': {
          from: { opacity: '0', transform: 'translateY(4px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'scale-in': {
          from: { opacity: '0', transform: 'scale(0.97)' },
          to: { opacity: '1', transform: 'scale(1)' },
        },
        'slide-in-right': {
          from: { transform: 'translateX(100%)' },
          to: { transform: 'translateX(0)' },
        },
        shimmer: {
          '100%': { transform: 'translateX(100%)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 150ms ease-out',
        'fade-in-up': 'fade-in-up 180ms ease-out',
        'scale-in': 'scale-in 150ms ease-out',
        'slide-in-right': 'slide-in-right 200ms ease-out',
      },
    },
  },
};

export default preset;
