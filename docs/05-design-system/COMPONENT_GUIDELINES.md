# Component Guidelines

Reusable components live in `packages/ui` and are imported by subpath, e.g.
`import { Button } from '@drawly/ui/Button'`. They are token-based, support light
and dark, and expose hover/focus/disabled/loading states. Apps compose them —
they must not create per-screen one-off styles.

## Catalogue

- **Forms:** `Button`, `IconButton`, `Input`, `Textarea`, `Select`, `Checkbox`,
  `Switch`, `SearchInput`, `Field`, `Label`. Inputs `forwardRef` (react-hook-form
  friendly) and accept an `error` state.
- **Data display:** `Card`, `DashboardCard`, `StatCard`, `MetricCard`, `Metric`,
  `Badge`, `StatusBadge`, `Avatar`, `DataTable` (sorting + pagination + loading +
  empty), `Pagination`.
- **Feedback:** `Alert`, `Spinner`, `Loader`, `Skeleton`, `LoadingCard`,
  `EmptyState`.
- **Overlays:** `Modal`, `ConfirmDialog`, `Tooltip`, `Dropdown` (+ `useDisclosure`).
- **Navigation / layout:** `PageHeader`, `SectionTitle`, `Breadcrumb`, `Tabs`.
- **Theme:** `ThemeProvider`, `useTheme`, `ThemeToggle`, `themeInitScript`
  (from `@drawly/ui/theme`).

> Note: components are kept flat in `packages/ui/src` (the environment used for
> this sprint could not delete/move files to reorganise into subfolders).

## Usage examples

```tsx
import { Button } from '@drawly/ui/Button';
<Button variant="primary" leftIcon={<Plus size={16} />} loading={saving}>Crear</Button>

import { Field } from '@drawly/ui/Field';
import { Input } from '@drawly/ui/Input';
<Field label="Correo" error={errors.email?.message}>
  <Input type="email" {...register('email')} />
</Field>

import { StatusBadge } from '@drawly/ui/StatusBadge';
<StatusBadge label="Publicada" tone="success" />

import { DataTable, type Column } from '@drawly/ui/DataTable';
<DataTable columns={columns} rows={rows} getRowKey={(r) => r.id} pageSize={10} />
```

## States & tones

Tones: `neutral | primary | success | warning | info | danger` (Badge,
StatusBadge, StatCard, Alert). Domain code maps its own statuses to a tone so the
components stay generic. Every interactive element shows hover + a visible focus
ring (accessible keyboard navigation) and a disabled/loading state where relevant.
