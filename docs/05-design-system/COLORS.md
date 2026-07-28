# Colors

Drawly palette — Version 3.0 ("Minimalista Premium", Sprint 11.5). Primary is
**Indigo/Violet**, shifted further from blue toward violet than v2.0. All
colors are exposed as CSS variables and Tailwind tokens; **never hardcode
colors** — use the tokens.

## Palettes (50–900, complete for every color)

- **Primary — Indigo/Violet:** 50 `#F2F1FD` · 100 `#E5E3FB` · 200 `#CCC7F8` ·
  300 `#ADA3F2` · 400 `#8A7CEA` · 500 `#6C5CE0` · 600 `#5B3FDB` (DEFAULT
  light) · 700 `#4A30C2` · 800 `#3C279D` · 900 `#302079`
- **Success — Emerald:** 50 `#ECFDF5` … 600 `#059669` (DEFAULT light) …
  900 `#064E3B`
- **Warning — Amber:** 50 `#FFFBEB` … 600 `#D97706` (DEFAULT light) …
  900 `#78350F`
- **Danger — Red:** 50 `#FEF2F2` … 600 `#DC2626` (DEFAULT light) …
  900 `#7F1D1D`
- **Info — Sky:** 50 `#F0F9FF` … 600 `#0284C7` (DEFAULT light) …
  900 `#0C4A6E`
- **Prize/Winner — Gold:** 50 `#FDF8EC` … 600 `#A66F10` (DEFAULT light) …
  900 `#4A3210`. New in v3.0 — reserved for winner/prize/podium/draw-result
  moments (e.g. a `winner` ticket, an announced raffle result). **Never
  reuse `warning` for this** — warning means "pay attention", prize means
  "you won".
- **Neutral — Stone (warm gray):** 50 `#FAFAF9` … 500 `#78716C` … 900
  `#1C1917` · 950 `#0C0A09`. Deliberately warm (not blue-slate) — backs the
  warm-white default background.

## Semantic tokens

| Token | Light | Dark |
|-------|-------|------|
| `background` | stone-50 (`#FAFAF9`, warm white) | stone-950 |
| `surface` | white | stone-900 |
| `card` | white | stone-800 |
| `muted` | stone-100 | stone-800 |
| `border` | stone-200 | stone-800 |
| `border-strong` | stone-300 | stone-700 |
| `text-primary` | stone-900 | stone-50 |
| `text-secondary` | stone-600 | stone-300 |
| `text-muted` | stone-500 (WCAG AA, ≥4.5:1) | stone-400 (WCAG AA) |
| `primary` | indigo-600 | indigo-500 |
| `primary-hover` | indigo-700 | indigo-400 |
| `primary-fg` | white | white |
| `{success,warning,danger,info,prize}` | `*-600` | `*-500` |
| `{success,warning,danger,info,prize}-solid` | fixed dark shade (`*-700`, warning `*-800`) — same in both themes | same |
| `{success,warning,danger,info,prize}-fg` | white (safe on `-solid`) | white |
| `overlay` | stone-950, fixed both themes | stone-950 |
| `inverse` / `inverse-fg` | stone-800 / stone-50, fixed both themes | stone-800 / stone-50 |
| `ring` | indigo-500 | indigo-400 |

`text-muted` and the Switch thumb were retuned in v3.0 to fix a real WCAG AA
contrast failure found in the Sprint 11 audit (previously ~2.5:1 in light
mode). `*-solid`/`*-fg` are new: `TONE_SOLID` used to hardcode `text-white`
per tone, which failed AA for several tones in dark mode — `*-solid` always
picks a shade dark enough for white text, regardless of theme.

## Usage

Consume tokens via Tailwind utilities: `bg-primary text-primary-fg`,
`bg-card border-border`, `text-text-secondary`, `bg-success/10 text-success`,
`bg-success-solid text-success-fg` (filled/solid contexts — see
`ProgressBar`), `ring` for focus. Tinted backgrounds use alpha
(`bg-primary/10`). Any shade of any scale is reachable directly (e.g.
`bg-success-100`) when the semantic token isn't the right fit.

`Tone` (`packages/ui/src/tones.tsx`) is the shared type used by
`Badge`/`StatusBadge`/`StatCard`/`ProgressBar`/`Alert`:
`'neutral' | 'primary' | 'success' | 'warning' | 'info' | 'danger' | 'prize'`.
Domain code maps its own statuses to a `Tone` — e.g. a `winner` ticket maps
to `tone: 'prize'`, consistently in both the admin panel and the public
portal.

Source of truth: `apps/web/src/app/globals.css` (values) and
`packages/config/tailwind-preset.ts` (Tailwind mapping).
