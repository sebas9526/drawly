/**
 * Presentation helper: formats a numeric amount as Colombian Peso currency
 * (no decimals — COP is never quoted in cents in this product). Shared by
 * every admin screen that surfaces money (dashboard, tickets, collaborators).
 */
const CURRENCY_FORMATTER = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
});

export function formatCurrency(value: number): string {
  return CURRENCY_FORMATTER.format(value);
}
