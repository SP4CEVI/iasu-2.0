export function downloadTextFile(filename: string, content: string, mime = 'text/csv'): void {
  // BOM нужен, чтобы Excel корректно открыл кириллицу
  const blob = new Blob(['﻿', content], { type: `${mime};charset=utf-8` });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function toCsv(rows: (string | number | null | undefined)[][]): string {
  const escape = (cell: string | number | null | undefined) => {
    const text = String(cell ?? '');
    return /[";\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
  };
  return rows.map((row) => row.map(escape).join(';')).join('\n');
}
