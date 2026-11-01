import { request } from '@/shared/api';

export interface EnrollmentCode {
  code: string;
  teacher_id: number;
  teacher_name: string;
  expires_at: string;
}

export const createEnrollmentCode = (teacherId: number, expiresInHours: number) =>
  request<EnrollmentCode>('/v1/admin/enrollment-codes', {
    method: 'POST',
    body: { teacher_id: teacherId, expires_in_hours: expiresInHours },
  });
