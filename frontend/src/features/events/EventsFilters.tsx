import { InputField, SelectField } from '@/shared/ui';
import type { FilterValues } from './filters';
import { EVENT_TYPES } from './types';

interface EventsFiltersProps {
  filters: FilterValues;
  onChange: (name: keyof FilterValues, value: string) => void;
}

const TEXT_FILTERS = ['device_id', 'uid', 'teacher_id', 'subject_id', 'group_id'] as const;

export function EventsFilters({ filters, onChange }: EventsFiltersProps) {
  return (
    <>
      <div className="toolbar">
        <SelectField
          label="Severity"
          value={filters.severity}
          onChange={(e) => onChange('severity', e.target.value)}
        >
          <option value="">Все</option>
          <option value="info">info</option>
          <option value="warning">warning</option>
          <option value="error">error</option>
        </SelectField>
        <SelectField
          label="Тип события"
          value={filters.event_type}
          onChange={(e) => onChange('event_type', e.target.value)}
        >
          <option value="">Все типы</option>
          {EVENT_TYPES.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </SelectField>
        <InputField
          label="Дата"
          type="date"
          value={filters.date}
          onChange={(e) => onChange('date', e.target.value)}
        />
      </div>
      <div className="toolbar toolbar--grid">
        {TEXT_FILTERS.map((name) => (
          <InputField
            key={name}
            label={name}
            placeholder="Любой"
            value={filters[name]}
            onChange={(e) => onChange(name, e.target.value)}
          />
        ))}
      </div>
    </>
  );
}
