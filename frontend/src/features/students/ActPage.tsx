import { Link, useSearchParams } from 'react-router-dom';
import { formatDate } from '@/shared/library';
import { Button, PageHeader } from '@/shared/ui';
import { useAuth } from '../auth';

export function ActPage() {
  const [params] = useSearchParams();
  const { login } = useAuth();
  const document = params.get('doc') ?? '—';
  const date = formatDate(params.get('date'));

  return (
    <>
      <div className="no-print">
        <PageHeader
          title="Акт об уничтожении персональных данных"
          subtitle="Формируется после отзыва согласия. Распечатывается, подписывается и хранится в деле."
          actions={
            <>
              <Link to="/students" className="btn btn--secondary">
                Назад к списку
              </Link>
              <Button onClick={() => window.print()}>Распечатать</Button>
            </>
          }
        />
      </div>
      <article className="act">
        <h1>АКТ ОБ УНИЧТОЖЕНИИ ПЕРСОНАЛЬНЫХ ДАННЫХ</h1>
        <p>Дата: {date}</p>
        <p>Оператор: ФГАОУ ВО МАИ</p>
        <p>
          На основании заявления №{document} от {date} об отзыве согласия произведено уничтожение
          персональных данных студента:
        </p>
        <p>
          — ФИО
          <br />— UID пропуска
        </p>
        <p>
          Записи о посещаемости сохранены в обезличенном виде. Восстановление персональных данных
          невозможно.
        </p>
        <p style={{ marginTop: 40 }}>Ответственный: {login ?? '[ФИО админа]'}</p>
        <p>Подпись: ____________</p>
      </article>
    </>
  );
}
