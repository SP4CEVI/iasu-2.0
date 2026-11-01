const KEY = 'attendance.admin.token';

let unauthorizedHandler: (() => void) | null = null;

export function getToken(): string | null {
  try {
    return localStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string | null): void {
  try {
    if (token) {
      localStorage.setItem(KEY, token);
    } else {
      localStorage.removeItem(KEY);
    }
  } catch {
  }
}

export function onUnauthorized(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
}

export function notifyUnauthorized(): void {
  unauthorizedHandler?.();
}
