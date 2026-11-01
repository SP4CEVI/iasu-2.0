import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { errorMessage } from '@/shared/api';
import { formatDate, todayIso } from '@/shared/library';
import { Button, InputField, Modal, Notice } from '@/shared/ui';
import { revokeConsent, type Student } from './api';
import { studentLabel } from './display';

interface RevokeModalProps {
  student: Student;
  onClose: () => void;
  onRevoked: () => void;
}

interface RevokeForm {
  document: string;
  date: string;
}

export function RevokeModal({ student, onClose, onRevoked }: RevokeModalProps) {
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RevokeForm>({ defaultValues: { date: todayIso() } });

  const onSubmit = handleSubmit(async (values) => {
    setServerError(null);
    try {
      await revokeConsent(student.id, {
        revocation_document: values.document.trim(),
        revocation_date: values.date,
      });
      onRevoked();
    } catch (error) {
      setServerError(errorMessage(error));
    }
  });

  return (
    <Modal title="Отзыв согласия" onClose={onClose}>
      <form onSubmit={onSubmit} noValidate>
        <div className="summary">
          <strong>{studentLabel(student)}</strong>{' '}
          <span className="muted">
            {student.group_name} · согласие №{student.consent_document} от{' '}
            {formatDate(student.consent_date)}
          </span>
        </div>
        {serverError && <Notice tone="error">{serverError}</Notice>}
        <div className="field-row">
          <InputField
            label="Номер заявления"
            error={errors.document?.message}
            {...register('document', { required: 'Укажите номер' })}
          />
          <InputField
            label="Дата заявления"
            type="date"
            error={errors.date?.message}
            {...register('date', { required: 'Укажите дату' })}
          />
        </div>
        <Notice tone="warning">
          <strong>Что произойдёт</strong>
          <br />
          ФИО и UID студента будут обнулены. Записи посещаемости сохранятся в обезличенном виде.
          Срок обработки после отзыва — не более 30 дней.
        </Notice>
        <div className="modal__footer">
          <Button variant="secondary" onClick={onClose}>
            Отмена
          </Button>
          <Button type="submit" variant="danger" loading={isSubmitting}>
            Отозвать согласие
          </Button>
        </div>
      </form>
    </Modal>
  );
}
