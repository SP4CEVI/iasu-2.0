import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { errorMessage } from '@/shared/api';
import { useRequest } from '@/shared/library';
import { Badge, Button, DataState, Notice, PageHeader, Pagination } from '@/shared/ui';
import { fetchEvents, type EventEntry } from './api';
import { contextText, relatedEntities } from './entities';
import { EventPanel } from './EventPanel';
import { EventsFilters } from './EventsFilters';
import { exportEventsCsv } from './export';
import {
  applyLocalFilters,
  EMPTY_FILTERS,
  noteLocalFilter,
  toApiFilters,
  type FilterValues,
} from './filters';
import { severityTone } from './severity';

const PAGE_SIZE = 50;
const REFRESH_MS = 30_000;

function formatEventTime(value: string): string {
  const date = new Date(value);
  const pad = (n: number) => String(n).padStart(2, '0');
  const day = `${pad(date.getDate())}.${pad(date.getMonth() + 1)}`;
  return `${day} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function EventRow({ entry, onOpen }: { entry: EventEntry; onOpen: () => void }) {
  const entities = relatedEntities(entry);
  return (
    <tr className={`row-clickable row--${entry.severity}`} onClick={onOpen}>
      <td>{formatEventTime(entry.timestamp)}</td>
      <td>
        <Badge tone={severityTone(entry.severity)}>{entry.severity}</Badge>
      </td>
      <td>{entry.event_type}</td>
      <td>{contextText(entry) || '—'}</td>
      <td>
        {entities.length === 0 && <span className="muted">—</span>}
        {entities.map((entity) => (
          <div key={entity.label}>
            <Link to={entity.to} className="link" onClick={(event) => event.stopPropagation()}>
              {entity.label} {entity.value}
            </Link>
          </div>
        ))}
      </td>
    </tr>
  );
}

export function EventsPage() {
  const [filters, setFilters] = useState<FilterValues>(EMPTY_FILTERS);
  const [page, setPage] = useState(1);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selected, setSelected] = useState<EventEntry | null>(null);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const apiFilters = toApiFilters(filters);
  const events = useRequest(
    () => fetchEvents({ ...apiFilters, page, size: PAGE_SIZE }),
    `events:${page}:${JSON.stringify(apiFilters)}`,
  );
  const items = applyLocalFilters(events.data?.items ?? [], filters);

  const reloadRef = useRef(events.reload);
  useEffect(() => {
    reloadRef.current = events.reload;
  });
  useEffect(() => {
    if (!autoRefresh) {
      return;
    }
    const timer = setInterval(() => reloadRef.current(), REFRESH_MS);
    return () => clearInterval(timer);
  }, [autoRefresh]);

  const changeFilter = (name: keyof FilterValues, value: string) => {
    noteLocalFilter(name, value);
    setFilters((current) => ({ ...current, [name]: value }));
    setPage(1);
  };

  const onExport = async () => {
    setExporting(true);
    setExportError(null);
    try {
      await exportEventsCsv(apiFilters);
    } catch (error) {
      setExportError(errorMessage(error));
    } finally {
      setExporting(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Журнал событий"
        subtitle="Неуспешные попытки и важные действия. Единственная точка доступа к логам."
        actions={
          <>
            <label className="switch">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
              Автообновление раз в 30 с
            </label>
            <Button variant="secondary" loading={exporting} onClick={onExport}>
              Экспорт в CSV
            </Button>
          </>
        }
      />
      {exportError && <Notice tone="error">{exportError}</Notice>}
      <EventsFilters filters={filters} onChange={changeFilter} />

      <DataState
        loading={events.loading}
        error={events.error}
        empty={items.length === 0}
        emptyText="Событий не найдено"
        onRetry={events.reload}
      >
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Время</th>
                <th>Severity</th>
                <th>Тип события</th>
                <th>Контекст</th>
                <th>Связанные сущности</th>
              </tr>
            </thead>
            <tbody>
              {items.map((entry) => (
                <EventRow key={entry.id} entry={entry} onOpen={() => setSelected(entry)} />
              ))}
            </tbody>
          </table>
          <Pagination
            page={page}
            size={PAGE_SIZE}
            total={events.data?.total ?? 0}
            onChange={setPage}
          />
        </div>
      </DataState>

      {selected && <EventPanel entry={selected} onClose={() => setSelected(null)} />}
    </>
  );
}