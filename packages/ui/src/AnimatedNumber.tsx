'use client';

import { useEffect, useRef, useState } from 'react';

interface AnimatedNumberProps {
  value: number;
  duration?: number;
  formatter?: (value: number) => string;
}

/** Eases a numeric value from its previous render to the new one. Purely
 * cosmetic — never the source of truth for the number it displays. */
export function AnimatedNumber({
  value,
  duration = 600,
  formatter,
}: AnimatedNumberProps): React.JSX.Element {
  const [display, setDisplay] = useState(value);
  const fromRef = useRef(value);

  useEffect(() => {
    const from = fromRef.current;
    const to = value;
    if (from === to) return;

    let frame = 0;
    const start = performance.now();

    const tick = (now: number): void => {
      const progress = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(from + (to - from) * eased));
      if (progress < 1) {
        frame = requestAnimationFrame(tick);
      } else {
        fromRef.current = to;
      }
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [value, duration]);

  return <>{formatter ? formatter(display) : display.toLocaleString('es-CO')}</>;
}
