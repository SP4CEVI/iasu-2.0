import type { BadgeTone } from '@/shared/ui';

const TONES: Record<string, BadgeTone> = {
  info: 'neutral',
  warning: 'warning',
  error: 'danger',
};

export function severityTone(severity: string): BadgeTone {
  return TONES[severity] ?? 'neutral';
}
