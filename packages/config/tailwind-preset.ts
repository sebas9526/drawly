import type { Config } from 'tailwindcss';

/**
 * Shared Tailwind preset carrying the Drawly design tokens
 * (see docs/05-design-system/COLORS.md and DESIGN_SYSTEM.md).
 * Colors reference CSS variables so apps can swap light/dark values
 * without duplicating the palette. Default Tailwind spacing already
 * matches the documented scale (4/8/12/16/24/32/48/64px), so it is
 * intentionally left untouched.
 */
const preset: Omit<Config, 'content'> = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'rgb(var(--color-primary) / <alpha-value>)',
          hover: 'rgb(var(--color-primary-hover) / <alpha-value>)',
        },
        secondary: 'rgb(var(--color-secondary) / <alpha-value>)',
        success: 'rgb(var(--color-success) / <alpha-value>)',
        warning: 'rgb(var(--color-warning) / <alpha-value>)',
        danger: 'rgb(var(--color-danger) / <alpha-value>)',
        info: 'rgb(var(--color-info) / <alpha-value>)',
        background: 'rgb(var(--color-background) / <alpha-value>)',
        surface: 'rgb(var(--color-surface) / <alpha-value>)',
        border: 'rgb(var(--color-border) / <alpha-value>)',
        'text-primary': 'rgb(var(--color-text-primary) / <alpha-value>)',
        'text-secondary': 'rgb(var(--color-text-secondary) / <alpha-value>)',
      },
      borderRadius: {
        DEFAULT: 'var(--radius)',
      },
      transitionDuration: {
        DEFAULT: '200ms',
      },
    },
  },
};

export default preset;
