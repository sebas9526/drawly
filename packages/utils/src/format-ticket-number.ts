/**
 * Presentation helper: zero-pads a ticket number to the width of the raffle's
 * largest generated number (e.g. starting at 1 with 1000 tickets -> "0001"..
 * "1000"; starting at 0 with 100 tickets -> "00".."99"). `maxNumber` is
 * `starting_number + total_tickets - 1`. The canonical value is the integer
 * stored by the API; padding is display-only. Shared by the admin and public
 * ticket views.
 */
export function formatTicketNumber(value: number, maxNumber: number): string {
  const width = Math.max(String(Math.max(maxNumber, 0)).length, 1);
  return String(value).padStart(width, '0');
}
