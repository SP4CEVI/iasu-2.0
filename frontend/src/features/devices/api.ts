import { request, type Page, type PageParams } from '@/shared/api';

export interface Device {
  id: string;
  teacher_id: number;
  teacher_name: string;
  active: boolean;
  created_at: string;
}

export interface DeviceFilters extends PageParams {
  teacher_id?: number;
  active?: boolean;
}

export const fetchDevices = (filters: DeviceFilters) =>
  request<Page<Device>>('/v1/admin/devices', { query: { ...filters } });

export const revokeDevice = (id: string) =>
  request<{ id: string; active: boolean }>(`/v1/admin/devices/${encodeURIComponent(id)}/revoke`, {
    method: 'POST',
  });
