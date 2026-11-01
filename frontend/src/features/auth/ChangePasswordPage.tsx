import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { errorMessage } from '@/shared/api';
import { Button, InputField, Notice, PageHeader } from '@/shared/ui';
import { changePassword } from './api';

const MIN_PASSWORD_LENGTH = 10;

interface PasswordForm {
  current: string;
  next: string;
  repeat: string;
}

export function ChangePasswordPage() {
  const navigate = useNavigate();
  const [result, setResult] = useState<{ tone: 'success' | 'error'; text: string } | null>(null);
  const {
    register,
    handleSubmit,
    getValues,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<PasswordForm>();

  const onSubmit = handleSubmit(async (values) => {
    setResult(null);
    try {
      await changePassword(values.current, values.next);
      reset();
      setResult({ tone: 'success', text: 'Пароль изменён' });
    } catch (error) {
      setResult({ tone: 'error', text: errorMessage(error) });
    }
  });

  return (
    <>
      <PageHeader title="Смена пароля" subtitle="Новый пароль хранится в виде bcrypt-хеша." />
      <form className="card" style={{ maxWidth: 480 }} onSubmit={onSubmit} noValidate>
        {result && <Notice tone={result.tone}>{result.text}</Notice>}
        <InputField
          label="Текущий пароль"
          type="password"
          autoComplete="current-password"
          error={errors.current?.message}
          {...register('current', { required: 'Введите текущий пароль' })}
        />
        <InputField
          label="Новый пароль"
          type="password"
          autoComplete="new-password"
          error={errors.next?.message}
          {...register('next', {
            required: 'Введите новый пароль',
            minLength: {
              value: MIN_PASSWORD_LENGTH,
              message: `Минимум ${MIN_PASSWORD_LENGTH} символов`,
            },
          })}
        />
        <InputField
          label="Повторите новый пароль"
          type="password"
          autoComplete="new-password"
          hint={`Минимум ${MIN_PASSWORD_LENGTH} символов. Не используйте пароль от других сервисов.`}
          error={errors.repeat?.message}
          {...register('repeat', {
            validate: (value) => value === getValues('next') || 'Пароли не совпадают',
          })}
        />
        <div className="btn-row">
          <Button type="submit" loading={isSubmitting}>
            Сменить пароль
          </Button>
          <Button variant="secondary" onClick={() => navigate('/students')}>
            Отмена
          </Button>
        </div>
      </form>
    </>
  );
}
