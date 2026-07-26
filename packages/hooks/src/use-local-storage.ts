import { useCallback, useEffect, useState } from 'react';

/**
 * Browser-only, SSR/hydration-safe. State always starts at `initialValue` —
 * matching what the server renders — and syncs from `window.localStorage`
 * only after mount, in an effect. Reading storage synchronously in the
 * initial render (the naive approach) would make the client's first paint
 * disagree with the server's, since the server has no `localStorage` to read
 * and always falls back to `initialValue`; a client that resolves the real
 * stored value on that same first paint triggers a React hydration mismatch.
 */
export function useLocalStorage<TValue>(
  key: string,
  initialValue: TValue,
): [TValue, (value: TValue) => void] {
  const [value, setValue] = useState<TValue>(initialValue);

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(key);
      if (stored !== null) setValue(JSON.parse(stored) as TValue);
    } catch {
      // Storage unavailable (private mode, disabled) — keep initialValue.
    }
  }, [key]);

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
