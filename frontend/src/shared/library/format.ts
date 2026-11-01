const DATE_ONLY = /^(\d{4})-(\d{2})-(\d{2})$/;

export function formatDate(value: string | null | undefined): string {
  if (!value) {
    return '—';
  }
  const match = DATE_ONLY.exec(value);
  if (match) {
    return `${match[3]}.${match[2]}.${match[1]}`;
  }
  return formatDateTime(value);
}

/** ISO-время → `01.09.2026 09:05`. */
export function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return '—';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  const pad = (n: number) => String(n).padStart(2, '0');
  const day = `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()}`;
  return `${day} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function formatTime(value: string | null | undefined): string {
  return value ? value.slice(0, 5) : '—';
}

export function todayIso(): string {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}
