import { downloadTextFile, formatDateTime, toCsv } from '@/shared/library';
import { fetchEvents, type EventEntry, type EventFilters } from './api';

const EXPORT_PAGE_SIZE = 200;
const EXPORT_MAX_PAGES = 50;

export async function exportEventsCsv(filters: EventFilters): Promise<number> {
  const rows: EventEntry[] = [];
  for (let page = 1; page <= EXPORT_MAX_PAGES; page += 1) {
    const result = await fetchEvents({ ...filters, page, size: EXPORT_PAGE_SIZE });
    rows.push(...result.items);
    if (rows.length >= result.total || result.items.length === 0) {
      break;
    }
  }
  const csv = toCsv([
    ['ID', 'Время', 'Тип', 'Важность', 'Данные'],
    ...rows.map((row) => [
      row.id,
      formatDateTime(row.timestamp),
      row.event_type,
      row.severity,
      JSON.stringify(row.meta),
    ]),
  ]);
  downloadTextFile(`event-log-${new Date().toISOString().slice(0, 10)}.csv`, csv);
  return rows.length;
}
