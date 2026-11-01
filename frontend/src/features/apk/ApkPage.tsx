import { useRequest } from '@/shared/library';
import { PageHeader } from '@/shared/ui';
import { fetchMeta } from '../auth';
import { ApkCard } from './ApkCard';

const STEPS = [
  'Откройте ссылку на телефоне с Android и скачайте файл.',
  'Разрешите установку из этого источника и установите приложение.',
  'При первом запуске введите одноразовый код регистрации.',
  'При обновлении скачайте новый файл и установите поверх старой версии — повторная регистрация не потребуется, данные устройства сохранятся.',
];

export function ApkPage() {
  const meta = useRequest(fetchMeta, 'meta');

  return (
    <>
      <PageHeader
        title="Приложение (APK)"
        subtitle="Ссылки для преподавателей. Файлы лежат в статике на том же хостинге, что и API."
      />
      <div className="grid-2">
        <ApkCard
          key={meta.loading ? 'loading' : 'ready'}
          title="Release-APK"
          description="Для преподавателей. При выпуске новой версии обновите ссылку — старая версия заменится поверх."
          initialUrl={meta.data?.apk_download_url ?? ''}
          placeholder="https://<хостинг>/static/attendance-release.apk"
          action="Обновление ссылки на release-APK"
        />
        <ApkCard
          title="Тестовая APK"
          description="Для QA и команды. Подключается к тестовому API."
          initialUrl=""
          placeholder="https://<тест-хостинг>/static/attendance-test.apk"
          action="Обновление ссылки на тестовую APK"
        />
      </div>
      <section className="card" style={{ marginTop: 24 }}>
        <h2>Как преподавателю установить и обновить приложение</h2>
        <ol className="steps" style={{ paddingLeft: 20 }}>
          {STEPS.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </section>
    </>
  );
}
