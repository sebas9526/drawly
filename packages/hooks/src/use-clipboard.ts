import { useCallback, useState } from 'react';

export interface UseClipboardResult {
  copy: (text: string) => Promise<boolean>;
  copied: boolean;
}

/** `copied` resets to false after `resetAfterMs`. */
export function useClipboard(resetAfterMs = 2000): UseClipboardResult {
  const [copied, setCopied] = useState(false);

  const copy = useCallback(
    async (text: string): Promise<boolean> => {
      try {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), resetAfterMs);
        return true;
      } catch {
        setCopied(false);
        return false;
      }
    },
    [resetAfterMs],
  );

  return { copy, copied };
}
