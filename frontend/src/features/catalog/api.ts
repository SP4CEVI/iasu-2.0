import { request } from '@/shared/api';

export interface Group {
  id: number;
  name: string;
}

export interface Teacher {
  id: number;
  last_name: string;
  first_name: string;
  middle_name: string | null;
  uid: string;
  full_name: string;
}

export const fetchGroups = () => request<Group[]>('/v1/admin/groups');
export const fetchTeachers = () => request<Teacher[]>('/v1/admin/teachers');
