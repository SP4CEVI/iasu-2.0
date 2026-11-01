import type { ReactNode } from 'react';

interface NoticeProps {
  tone?: 'info' | 'success' | 'error' | 'warning';
  children: ReactNode;
}

export function Notice({ tone = 'info', children }: NoticeProps) {
  return (
    <div className={`notice notice--${tone}`} role={tone === 'error' ? 'alert' : 'status'}>
      {children}
    </div>
  );
}
