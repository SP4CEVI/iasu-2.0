import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { errorMessage } from '@/shared/api';
import { Button, InputField, LogoMark, Notice } from '@/shared/ui';
import { useAuth } from './useAuth';

interface LoginForm {
  login: string;
  password: string;
}

export function LoginPage() {
  const { isAuthenticated, signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>();

  const target = (location.state as { from?: string } | null)?.from ?? '/students';
  if (isAuthenticated) {
    return <Navigate to={target} replace />;
  }

  const onSubmit = handleSubmit(async (values) => {
    setServerError(null);
    try {
      await signIn(values.login.trim(), values.password);
      navigate(target, { replace: true });
    } catch (error) {
      setServerError(errorMessage(error));
    }
  });

  return (
    <div className="auth-page">
      <form className="card auth-card" onSubmit={onSubmit} noValidate>
        <LogoMark size={48} />
        <h1>Вход в админ-панель</h1>
        <p className="muted">
          Система учёта посещаемости. Войдите под учётной записью администратора.
        </p>
        {serverError && <Notice tone="error">{serverError}</Notice>}
        <InputField
          label="Логин"
          autoComplete="username"
          error={errors.login?.message}
          {...register('login', { required: 'Введите логин' })}
        />
        <InputField
          label="Пароль"
          type="password"
          autoComplete="current-password"
          error={errors.password?.message}
          {...register('password', { required: 'Введите пароль' })}
        />
        <Button type="submit" className="btn--block" loading={isSubmitting}>
          Войти
        </Button>
      </form>
    </div>
  );
}
