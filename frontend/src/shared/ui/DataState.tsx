import type { ReactNode } from 'react';
import { Button } from './Button';
import { Notice } from './Notice';

interface DataStateProps {
  loading: boolean;
  error?: string;
  empty?: boolean;
  emptyText?: string;
  onRetry?: () => void;
  children: ReactNode;
}

export function DataState({
  loading,
  error,
  empty,
  emptyText = 'Нет данных',
  onRetry,
  children,
}: DataStateProps) {
  if (error) {
    return (
      <div className="state">
        <Notice tone="error">{error}</Notice>
        {onRetry && (
          <Button variant="secondary" onClick={onRetry}>
            Повторить
          </Button>
        )}
      </div>
    );
  }
  if (loading && empty !== false) {
    return <div className="state state--muted">Загрузка…</div>;
  }
  if (empty) {
    return <div className="state state--muted">{emptyText}</div>;
  }
  return <>{children}</>;
}
