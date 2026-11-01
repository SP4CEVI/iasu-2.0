import { request } from './http';

export async function checkHealth(): Promise<boolean> {
  try {
    const result = await request<{ status: string }>('/health', { raw: true, anonymous: true });
    return result.status === 'ok';
  } catch {
    return false;
  }
}
