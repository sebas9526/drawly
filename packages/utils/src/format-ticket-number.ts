/**
 * Presentation helper: zero-pads a ticket number to the width of the raffle's
 * largest number (e.g. total 1000 -> "0001".."1000"). The canonical value is
 * the integer stored by the API; padding is display-only. Shared by the admin
 * and public ticket views.
 */
export function formatTicketNumber(value: number, total: number): string {
  const width = Math.max(String(Math.max(total, 1)).length, 1);
  return String(value).padStart(width, '0');
}
