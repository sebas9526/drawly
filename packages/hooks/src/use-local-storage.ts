import { useCallback, useState } from 'react';

/**
 * Browser-only. Falls back to in-memory state (no persistence) when
 * `window.localStorage` is unavailable (SSR, private browsing, etc.).
 */
export function useLocalStorage<TValue>(
  key: string,
  initialValue: TValue,
): [TValue, (value: TValue) => void] {
  const [value, setValue] = useState<TValue>(() => {
    if (typeof window === 'undefined') return initialValue;

    try {
      const stored = window.localStorage.getItem(key);
      return stored ? (JSON.parse(stored) as TValue) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setStoredValue = useCallback(
    (next: TValue) => {
      setValue(next);

      if (typeof window === 'undefined') return;

      try {
        window.localStorage.setItem(key, JSON.stringify(next));
      } catch {
        // Storage unavailable (quota exceeded, private mode) — state still updates in memory.
      }
    },
    [key],
  );

  return [value, setStoredValue];
}
