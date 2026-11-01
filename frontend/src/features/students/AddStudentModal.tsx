import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { errorMessage } from '@/shared/api';
import { logNoApi, todayIso } from '@/shared/library';
import { Button, InputField, Modal, Notice, SelectField } from '@/shared/ui';
import type { Group } from '../catalog';
import { createStudent } from './api';

interface AddStudentModalProps {
  groups: Group[];
  onClose: () => void;
  onCreated: () => void;
}

interface AddStudentForm {
  fullName: string;
  groupId: string;
  uid: string;
  consentDocument: string;
  consentDate: string;
}

export function AddStudentModal({ groups, onClose, onCreated }: AddStudentModalProps) {
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AddStudentForm>({ defaultValues: { consentDate: todayIso() } });

  const onSubmit = handleSubmit(async (values) => {
    setServerError(null);
    try {
      logNoApi('Добавление студента: ФИО не отправлено', { fullName: values.fullName });
      await createStudent({
        uid: values.uid.trim(),
        group_id: Number(values.groupId),
        consent_document: values.consentDocument.trim(),
        consent_date: values.consentDate,
      });
      onCreated();
    } catch (error) {
      setServerError(errorMessage(error));
    }
  });

  return (
    <Modal title="Добавить студента" onClose={onClose}>
      <form onSubmit={onSubmit} noValidate>
        <p className="muted" style={{ marginBottom: 16 }}>
          Все поля обязательны. Бумажное согласие хранится в деле вуза, в системе фиксируются его
          номер и дата.
        </p>
        {serverError && <Notice tone="error">{serverError}</Notice>}
        <InputField
          label="ФИО"
          error={errors.fullName?.message}
          {...register('fullName', { required: 'Укажите ФИО' })}
        />
        <div className="field-row">
          <SelectField
            label="Группа"
            error={errors.groupId?.message}
            {...register('groupId', { required: 'Выберите группу' })}
          >
            <option value="">Выберите…</option>
            {groups.map((group) => (
              <option key={group.id} value={group.id}>
                {group.name}
              </option>
            ))}
          </SelectField>
          <InputField
            label="UID пропуска"
            error={errors.uid?.message}
            {...register('uid', { required: 'Укажите UID' })}
          />
        </div>
        <div className="field-row">
          <InputField
            label="Номер согласия"
            error={errors.consentDocument?.message}
            {...register('consentDocument', { required: 'Укажите номер' })}
          />
          <InputField
            label="Дата согласия"
            type="date"
            error={errors.consentDate?.message}
            {...register('consentDate', { required: 'Укажите дату' })}
          />
        </div>
        <div className="modal__footer">
          <Button variant="secondary" onClick={onClose}>
            Отмена
          </Button>
          <Button type="submit" loading={isSubmitting}>
            Добавить
          </Button>
        </div>
      </form>
    </Modal>
  );
}
