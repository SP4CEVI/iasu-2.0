/**
 * Действие, для которого в бэкенде ещё нет API: интерфейс работает как обычно,
 * а само действие пишется в консоль браузера. Когда эндпоинт появится — заменить вызов запросом.
 */
export function logNoApi(action: string, payload?: unknown): void {
  console.info(`[нет API] ${action}`, payload ?? '');
}
