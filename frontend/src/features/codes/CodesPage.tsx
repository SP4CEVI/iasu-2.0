import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { errorMessage } from '@/shared/api';
import { Button, Notice, PageHeader, SelectField } from '@/shared/ui';
import { useTeachers } from '../catalog';
import { createEnrollmentCode, type EnrollmentCode } from './api';

const CODE_TTL_HOURS = 24;

interface CodeForm {
  teacherId: string;
}

export function CodesPage() {
  const teachers = useTeachers();
  const [issued, setIssued] = useState<EnrollmentCode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CodeForm>();

  const onSubmit = handleSubmit(async (values) => {
    setError(null);
    setCopied(false);
    try {
      setIssued(await createEnrollmentCode(Number(values.teacherId), CODE_TTL_HOURS));
    } catch (e) {
      setIssued(null);
      setError(errorMessage(e));
    }
  });

  const copy = async () => {
    if (!issued) {
      return;
    }
    try {
      await navigator.clipboard.writeText(issued.code);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Коды регистрации"
        subtitle="Одноразовый код для привязки Android-устройства преподавателя."
      />
      <div className="grid-2">
        <form className="card" onSubmit={onSubmit} noValidate>
          <h2>Новый код</h2>
          {error && <Notice tone="error">{error}</Notice>}
          {teachers.error && <Notice tone="error">{teachers.error}</Notice>}
          <SelectField
            label="Преподаватель"
            error={errors.teacherId?.message}
            {...register('teacherId', { required: 'Выберите преподавателя' })}
          >
            <option value="">Выберите…</option>
            {(teachers.data ?? []).map((teacher) => (
              <option key={teacher.id} value={teacher.id}>
                {teacher.full_name}
              </option>
            ))}
          </SelectField>
          <Button type="submit" className="btn--block" loading={isSubmitting}>
            Сгенерировать код
          </Button>
          <p className="card-hint">
            Устройство регистрируется один раз: код привязывает его к выбранному преподавателю.
          </p>
        </form>

        {issued && (
          <section className="card card--success" aria-live="polite">
            <strong style={{ color: 'var(--success)', fontSize: 12 }}>Код создан</strong>
            <p className="muted" style={{ marginTop: 8 }}>
              Для: {issued.teacher_name}
            </p>
            <div className="code-box">{issued.code}</div>
            <Notice tone="warning">
              Код показывается один раз. Скопируйте его и передайте преподавателю: повторно показать
              код нельзя. Если нужен новый — сгенерируйте заново.
            </Notice>
            <Button variant="secondary" className="btn--block" onClick={copy}>
              {copied ? 'Скопировано' : 'Копировать код'}
            </Button>
          </section>
        )}
      </div>
    </>
  );
}
