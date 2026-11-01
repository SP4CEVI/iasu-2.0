import { request, type Page, type PageParams } from '@/shared/api';

export type Severity = 'info' | 'warning' | 'error';

export interface EventEntry {
  id: number;
  event_type: string;
  severity: Severity | string;
  meta: Record<string, unknown>;
  timestamp: string;
}

export interface EventFilters extends PageParams {
  severity?: string;
  event_type?: string;
  date_from?: string;
  date_to?: string;
  device_id?: string;
  uid?: string;
}

export function fetchEvents(filters: EventFilters) {
  const { device_id, uid, ...rest } = filters;
  return request<Page<EventEntry>>('/v1/admin/event-log', {
    query: { ...rest, 'meta.device_id': device_id, 'meta.uid': uid },
  });
}
