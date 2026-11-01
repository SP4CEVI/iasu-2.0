import type { EventEntry } from './api';

export interface RelatedEntity {
  label: string;
  value: string;
  to: string;
}

/** Связанные сущности события, найденные в meta. */
export function relatedEntities(entry: EventEntry): RelatedEntity[] {
  const { device_id, teacher_id, student_id } = entry.meta;
  const result: RelatedEntity[] = [];
  if (device_id) {
    result.push({
      label: 'Устройство',
      value: String(device_id),
      to: `/devices?id=${encodeURIComponent(String(device_id))}`,
    });
  }
  if (teacher_id) {
    result.push({
      label: 'Преподаватель',
      value: `#${String(teacher_id)}`,
      to: `/devices?teacher_id=${String(teacher_id)}`,
    });
  }
  if (student_id) {
    result.push({
      label: 'Студент',
      value: `#${String(student_id)}`,
      to: `/students?id=${String(student_id)}`,
    });
  }
  return result;
}

export function contextText(entry: EventEntry): string {
  return Object.entries(entry.meta)
    .map(([key, value]) => `${key}: ${String(value)}`)
    .join(' · ');
}