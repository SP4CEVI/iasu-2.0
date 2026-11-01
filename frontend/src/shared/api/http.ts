import { API_URL } from '../config/env';
import { ApiError } from './errors';
import { getToken, notifyUnauthorized } from './token';

type Query = Record<string, string | number | boolean | null | undefined>;

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  query?: Query;
  body?: unknown;
  /** Эндпоинт без токена (логин) — 401 не считается «сессия истекла». */
  anonymous?: boolean;
  /** Ответ без обёртки {status, data} (например, /health). */
  raw?: boolean;
}

interface Envelope<T> {
  status: 'ok' | 'error';
  data?: T;
  message?: string;
}

function buildUrl(path: string, query?: Query): string {
  const url = new URL(`${API_URL}${path}`);
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, String(value));
    }
  }
  return url.toString();
}

async function readJson(response: Response): Promise<Envelope<unknown> | null> {
  try {
    return (await response.json()) as Envelope<unknown>;
  } catch {
    return null;
  }
}

function buildHeaders(options: RequestOptions): Record<string, string> {
  const headers: Record<string, string> = {};
  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }
  const token = getToken();
  if (token && !options.anonymous) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

function toApiError(response: Response, json: Envelope<unknown> | null): ApiError | null {
  if (response.ok && json?.status !== 'error') {
    return null;
  }
  return new ApiError(json?.message ?? `Ошибка сервера (${response.status})`, response.status);
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(buildUrl(path, options.query), {
    method: options.method ?? 'GET',
    headers: buildHeaders(options),
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });
  const json = await readJson(response);

  if (response.status === 401 && !options.anonymous) {
    notifyUnauthorized();
  }
  const error = toApiError(response, json);
  if (error) {
    throw error;
  }
  return (options.raw ? json : json?.data) as T;
}
