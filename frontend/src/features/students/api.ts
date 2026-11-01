import { request, type Page, type PageParams } from '@/shared/api';

export type ConsentStatus = 'active' | 'revoked';

export interface StudentCard {
  id: number;
  uid: string | null;
  active: boolean;
  created_at: string;
}

export interface Student {
  id?: number;
  fio: string;
  group_id: number;
  group_name: string;
  cards: StudentCard[];
  consent_document: string;
  consent_date: string;
  revocation_document: string | null;
  revocation_date: string | null;
  anonymized_at: string | null;
  consent_status: ConsentStatus;
  created_at: string;
}

export interface StudentFilters extends PageParams {
  group_id?: number;
  consent_status?: ConsentStatus;
}

export interface NewStudent {
  uid: string;
  group_id: number;
  consent_document: string;
  consent_date: string;
}

export interface Revocation {
  revocation_document: string;
  revocation_date: string;
}

export const fetchStudents = (filters: StudentFilters) =>
  request<Page<Student>>('/v1/admin/students', { query: { ...filters } });

export const createStudent = (student: NewStudent) =>
  request<Student>('/v1/admin/students', { method: 'POST', body: student });

export const revokeConsent = (id: number, revocation: Revocation) =>
  request<Student>(`/v1/admin/students/${id}/revoke`, { method: 'POST', body: revocation });
