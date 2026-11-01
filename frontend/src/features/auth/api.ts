import { request } from '@/shared/api';

export interface LoginResult {
  access_token: string;
  token_type: string;
  login: string;
}

export interface AdminMeta {
  login: string;
  apk_download_url: string | null;
}

export function login(loginValue: string, password: string): Promise<LoginResult> {
  return request<LoginResult>('/v1/admin/login', {
    method: 'POST',
    body: { login: loginValue, password },
    anonymous: true,
  });
}

export function changePassword(currentPassword: string, newPassword: string): Promise<unknown> {
  return request('/v1/admin/change-password', {
    method: 'POST',
    body: { current_password: currentPassword, new_password: newPassword },
  });
}

export function fetchMeta(): Promise<AdminMeta> {
  return request<AdminMeta>('/v1/admin/meta');
}
