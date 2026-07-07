# Design System

Drawly Design System — Version 2.0 (Sprint UI/UX)

Identidad visual moderna tipo SaaS (inspirada en la calidad de Linear, Vercel,
Supabase, Stripe), con temas claro/oscuro, tokens de diseño y componentes
reutilizables en `packages/ui`.

---

## Tokens

Todo el estilo se consume a través de **design tokens** (variables CSS mapeadas a
utilidades de Tailwind en `packages/config/tailwind-preset.ts`). No se permiten
colores, tamaños, radios ni sombras hardcodeados.

- **Paletas** (RGB, 50–900, independientes del tema): `primary` (Indigo/Violet),
  `success` (Emerald), `warning` (Amber), `danger` (Red), `info` (Sky),
  `neutral` (Slate).
- **Tokens semánticos** (cambian entre claro/oscuro): `background`, `surface`,
  `card`, `muted`, `border`, `border-strong`, `text-primary`, `text-secondary`,
  `text-muted`, `primary` / `primary-hover` / `primary-fg`, `ring`.

Definidos en `apps/web/src/app/globals.css` (`:root` = claro, `.dark` = oscuro).

## Temas

Claro y oscuro con interruptor (`ThemeToggle`). La preferencia se persiste en
`localStorage` y respeta `prefers-color-scheme`. Un script inline aplica el tema
antes de la hidratación para evitar parpadeo. Todos los componentes soportan
ambos temas porque consumen tokens semánticos.

## Tipografía

Fuente **Inter** (`next/font`). Escala basada en utilidades de Tailwind:
`text-2xl`/`text-xl` (títulos), `text-sm`/`text-base` (cuerpo), `text-xs`
(captions), con pesos `font-medium`/`font-semibold`.

## Espaciado

Múltiplos de 4px (escala por defecto de Tailwind): 4, 8, 12, 16, 20, 24, 32, 40,
48, 64. No usar valores arbitrarios.

## Bordes (radios)

`xs` .25rem · `sm` .375rem · `md` .5rem · `lg` .75rem · `xl` 1rem · `2xl` 1.25rem.

## Sombras

`shadow-sm` · `shadow-md` · `shadow-lg` · `shadow-xl` (escala en el preset).

## Animaciones

Sutiles y rápidas: `animate-fade-in`, `fade-in-up`, `scale-in`, `slide-in-right`
+ `animate-pulse` para skeletons. Duración base de transición: 150ms.

## Iconografía

**Lucide React** exclusivamente. No mezclar librerías de iconos.

## Layout administrativo

`AppShell` (`apps/web/src/components/shell`): sidebar colapsable y persistente
(Dashboard, Rifas, Participantes + placeholders Boletas/Pagos/Reportes/
Configuración), topbar (logo, buscador placeholder, ThemeToggle, menú de
usuario), breadcrumbs y área principal. Responsive (drawer en móvil).

## Accesibilidad

WCAG AA, focus visible global (`:focus-visible` ring), navegación por teclado,
roles/ARIA en overlays (dialog, menu, switch, tooltip) y contraste por tokens.
