import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { errorMessage } from '@/shared/api';
import { formatDate, useRequest } from '@/shared/library';
import {
  Badge,
  Button,
  DataState,
  FilterChip,
  Modal,
  Notice,
  PageHeader,
  Pagination,
  SelectField,
} from '@/shared/ui';
import { useTeachers } from '../catalog';
import { fetchDevices, revokeDevice, type Device } from './api';

const PAGE_SIZE = 10;

function RevokeDeviceModal({ device, onClose, onRevoked }: RevokeProps) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const confirm = async () => {
    setBusy(true);
    setError(null);
    try {
      await revokeDevice(device.id);
      onRevoked();
    } catch (e) {
      setError(errorMessage(e));
      setBusy(false);
    }
  };

  return (
    <Modal title="Отозвать устройство?" onClose={onClose}>
      {error && <Notice tone="error">{error}</Notice>}
      <p>
        Устройство преподавателя {device.teacher_name} перестанет принимать отметки. Чтобы вернуть
        доступ, потребуется новый код регистрации.
      </p>
      <div className="modal__footer" style={{ marginTop: 20 }}>
        <Button variant="secondary" onClick={onClose}>
          Отмена
        </Button>
        <Button variant="danger" loading={busy} onClick={confirm}>
          Отозвать
        </Button>
      </div>
    </Modal>
  );
}

interface RevokeProps {
  device: Device;
  onClose: () => void;
  onRevoked: () => void;
}

export function DevicesPage() {
  const [params, setParams] = useSearchParams();
  const teacherId = params.get('teacher_id') ?? '';
  const deviceId = params.get('id') ?? '';
  const [active, setActive] = useState('');
  const [page, setPage] = useState(1);
  const [target, setTarget] = useState<Device | null>(null);
  const teachers = useTeachers();

  const setParam = (name: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value) {
      next.set(name, value);
    } else {
      next.delete(name);
    }
    setParams(next);
    setPage(1);
  };

  const size = deviceId ? 100 : PAGE_SIZE;
  const devices = useRequest(
    () =>
      fetchDevices({
        page,
        size,
        teacher_id: teacherId ? Number(teacherId) : undefined,
        active: active === '' ? undefined : active === 'true',
      }),
    `devices:${page}:${size}:${teacherId}:${active}`,
  );
  const items = (devices.data?.items ?? []).filter((d) => !deviceId || d.id === deviceId);

  return (
    <>
      <PageHeader
        title="Устройства"
        subtitle="Зарегистрированные Android-устройства преподавателей."
      />
      {deviceId && (
        <FilterChip text={`Устройство ${deviceId}`} onClear={() => setParam('id', '')} />
      )}
      <div className="toolbar">
        <SelectField
          label="Преподаватель"
          value={teacherId}
          onChange={(event) => setParam('teacher_id', event.target.value)}
        >
          <option value="">Все преподаватели</option>
          {(teachers.data ?? []).map((teacher) => (
            <option key={teacher.id} value={teacher.id}>
              {teacher.full_name}
            </option>
          ))}
        </SelectField>
        <SelectField
          label="Статус"
          value={active}
          onChange={(event) => {
            setActive(event.target.value);
            setPage(1);
          }}
        >
          <option value="">Все</option>
          <option value="true">Активно</option>
          <option value="false">Отозвано</option>
        </SelectField>
      </div>
      <DataState
        loading={devices.loading}
        error={devices.error}
        empty={items.length === 0}
        emptyText="Устройств не найдено"
        onRetry={devices.reload}
      >
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Идентификатор устройства</th>
                <th>Преподаватель</th>
                <th>Статус</th>
                <th>Дата регистрации</th>
                <th className="actions">Действие</th>
              </tr>
            </thead>
            <tbody>
              {items.map((device) => (
                <tr key={device.id}>
                  <td>{device.id}</td>
                  <td>{device.teacher_name}</td>
                  <td>
                    <Badge tone={device.active ? 'success' : 'neutral'}>
                      {device.active ? 'Активно' : 'Отозвано'}
                    </Badge>
                  </td>
                  <td>{formatDate(device.created_at)}</td>
                  <td className="actions">
                    {device.active ? (
                      <Button
                        variant="secondary"
                        className="btn--small"
                        onClick={() => setTarget(device)}
                      >
                        Отозвать
                      </Button>
                    ) : (
                      <span className="muted">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <Pagination
            page={page}
            size={size}
            total={deviceId ? items.length : (devices.data?.total ?? 0)}
            onChange={setPage}
          />
        </div>
      </DataState>
      {target && (
        <RevokeDeviceModal
          device={target}
          onClose={() => setTarget(null)}
          onRevoked={() => {
            setTarget(null);
            devices.reload();
          }}
        />
      )}
    </>
  );
}