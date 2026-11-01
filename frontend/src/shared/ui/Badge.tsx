import type { ReactNode } from 'react';

export type BadgeTone = 'success' | 'danger' | 'warning' | 'neutral';

interface BadgeProps {
  tone?: BadgeTone;
  children: ReactNode;
}

export function Badge({ tone = 'neutral', children }: BadgeProps) {
  return <span className={`badge badge--${tone}`}>{children}</span>;
}
