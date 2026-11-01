import type { Student } from './api';

export function studentLabel(student: Student): string {
  return student.consent_status === 'revoked' ? 'Студент (обезличен)' : `${student.fio}`;
}

export function studentUid(student: Student): string {
  return student.cards.find((card) => card.uid)?.uid ?? '—';
}
