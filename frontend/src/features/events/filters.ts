import { logNoApi } from '@/shared/library';
import type { EventEntry, EventFilters } from './api';

export const EMPTY_FILTERS = {
  severity: '',
  event_type: '',
  date: '',
  device_id: '',
  uid: '',
  teacher_id: '',
  subject_id: '',
  group_id: '',
};

export type FilterValues = typeof EMPTY_FILTERS;

const LOCAL_KEYS = ['teacher_id', 'subject_id', 'group_id'] as const;

export function toApiFilters(values: FilterValues): EventFilters {
  return {
    severity: values.severity || undefined,
    event_type: values.event_type || undefined,
    date_from: values.date || undefined,
    date_to: values.date || undefined,
    device_id: values.device_id.trim() || undefined,
    uid: values.uid.trim() || undefined,
  };
}

export function applyLocalFilters(items: EventEntry[], values: FilterValues): EventEntry[] {
  return items.filter((entry) =>
    LOCAL_KEYS.every(
      (key) => !values[key].trim() || String(entry.meta[key] ?? '') === values[key].trim(),
    ),
  );
}

export function noteLocalFilter(name: keyof FilterValues, value: string): void {
  if ((LOCAL_KEYS as readonly string[]).includes(name) && value) {
    logNoApi(`Фильтр журнала по ${name}: на сервере не поддерживается`, { [name]: value });
  }
}
