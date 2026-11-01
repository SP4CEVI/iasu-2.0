import { useRequest } from '@/shared/library';
import { fetchGroups, fetchTeachers } from './api';

export function useGroups() {
  return useRequest(fetchGroups, 'groups');
}

export function useTeachers() {
  return useRequest(fetchTeachers, 'teachers');
}
