import { Link } from 'react-router-dom';
import { formatDateTime } from '@/shared/library';
import { Badge, Icon } from '@/shared/ui';
import type { EventEntry } from './api';
import { relatedEntities } from './entities';
import { severityTone } from './severity';
import { EVENT_DESCRIPTIONS } from './types';

interface EventPanelProps {
  entry: EventEntry;
  onClose: () => void;
}

export function EventPanel({ entry, onClose }: EventPanelProps) {
  const entities = relatedEntities(entry);
  const description = EVENT_DESCRIPTIONS[entry.event_type];

  return (
    <div className="drawer-backdrop" onMouseDown={onClose}>
      <aside className="drawer" aria-label="Событие" onMouseDown={(e) => e.stopPropagation()}>
        <div className="drawer__top">
          <span>Событие</span>
          <button type="button" className="icon-btn" aria-label="Закрыть" onClick={onClose}>
            <Icon name="close" />
          </button>
        </div>
        <div className="drawer__title">
          <h2 style={{ fontSize: 24 }}>{entry.event_type}</h2>
          <Badge tone={severityTone(entry.severity)}>{entry.severity}</Badge>
        </div>
        <p className="muted">
          {formatDateTime(entry.timestamp)}
          {description && ` · ${description}`}
        </p>

        <h3>Связанные сущности</h3>
        {entities.length === 0 && <p className="muted">Нет связанных сущностей</p>}
        {entities.map((entity) => (
          <div className="entity" key={entity.label}>
            <span>{entity.label}</span>
            <Link to={entity.to} className="link">
              {entity.value}
            </Link>
          </div>
        ))}

        <h3>meta</h3>
        <pre className="json">{JSON.stringify(entry.meta, null, 2)}</pre>
      </aside>
    </div>
  );
}
