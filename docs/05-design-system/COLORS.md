# Colors

Drawly palette — Version 2.0. Primary is **Indigo/Violet** (no corporate blue).
All colors are exposed as CSS variables and Tailwind tokens; **never hardcode
colors** — use the tokens.

## Palettes (50–900)

- **Primary — Indigo/Violet:** 50 `#EEF2FF` · 100 `#E0E7FF` · 200 `#C7D2FE` ·
  300 `#A5B4FC` · 400 `#818CF8` · 500 `#6366F1` · 600 `#4F46E5` (DEFAULT light) ·
  700 `#4338CA` · 800 `#3730A3` · 900 `#312E81`
- **Success — Emerald:** 500 `#10B981` · 600 `#059669`
- **Warning — Amber:** 500 `#F59E0B` · 600 `#D97706`
- **Danger — Red:** 500 `#EF4444` · 600 `#DC2626`
- **Info — Sky:** 500 `#0EA5E9` · 600 `#0284C7`
- **Neutral — Slate:** 50 `#F8FAFC` … 500 `#64748B` … 900 `#0F172A` · 950 `#020617`

## Semantic tokens

| Token | Light | Dark |
|-------|-------|------|
| `background` | slate-50 | slate-950 |
| `surface` | white | slate-900 |
| `card` | white | slate-800 |
| `muted` | slate-100 | slate-800 |
| `border` | slate-200 | slate-800 |
| `text-primary` | slate-900 | slate-50 |
| `text-secondary` | slate-600 | slate-400 |
| `text-muted` | slate-400 | slate-500 |
| `primary` | indigo-600 | indigo-500 |
| `primary-hover` | indigo-700 | indigo-400 |
| `primary-fg` | white | white |
| `ring` | indigo-500 | indigo-400 |

## Usage

Consume tokens via Tailwind utilities: `bg-primary text-primary-fg`,
`bg-card border-border`, `text-text-secondary`, `bg-success/10 text-success`,
`ring` for focus. Tinted backgrounds use alpha (`bg-primary/10`).

Source of truth: `apps/web/src/app/globals.css` (values) and
`packages/config/tailwind-preset.ts` (Tailwind mapping).
