import { Icon } from './Icon';

interface PaginationProps {
  page: number;
  size: number;
  total: number;
  onChange: (page: number) => void;
}

export function Pagination({ page, size, total, onChange }: PaginationProps) {
  const pages = Math.max(1, Math.ceil(total / size));
  const from = total === 0 ? 0 : (page - 1) * size + 1;
  const to = Math.min(page * size, total);

  return (
    <div className="pagination">
      <span className="muted">
        {from}–{to} из {total}
      </span>
      <div className="pagination__pages">
        <button
          type="button"
          className="page-btn"
          aria-label="Предыдущая страница"
          disabled={page <= 1}
          onClick={() => onChange(page - 1)}
        >
          <Icon name="left" size={16} />
        </button>
        <span>
          {page} / {pages}
        </span>
        <button
          type="button"
          className="page-btn"
          aria-label="Следующая страница"
          disabled={page >= pages}
          onClick={() => onChange(page + 1)}
        >
          <Icon name="right" size={16} />
        </button>
      </div>
    </div>
  );
}
