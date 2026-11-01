import { useEffect, useRef, useState } from 'react';
import { errorMessage } from '../api';

interface Settled<T> {
  key: string;
  data?: T;
  error?: string;
}

export function useRequest<T>(load: () => Promise<T>, key: string) {
  const [tick, setTick] = useState(0);
  const [settled, setSettled] = useState<Settled<T> | null>(null);
  const loadRef = useRef(load);
  const fullKey = `${key}#${tick}`;

  useEffect(() => {
    loadRef.current = load;
  });

  useEffect(() => {
    let cancelled = false;
    loadRef
      .current()
      .then((data) => !cancelled && setSettled({ key: fullKey, data }))
      .catch((error: unknown) => {
        if (!cancelled) {
          setSettled({ key: fullKey, error: errorMessage(error) });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [fullKey]);

  const isCurrent = settled?.key === fullKey;
  return {
    data: settled?.data,
    error: isCurrent ? settled.error : undefined,
    loading: !isCurrent,
    reload: () => setTick((value) => value + 1),
  };
}
