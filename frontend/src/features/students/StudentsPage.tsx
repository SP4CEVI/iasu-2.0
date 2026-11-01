import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { formatDate, useRequest } from '@/shared/library';
import {
  Badge,
  Button,
  DataState,
  FilterChip,
  PageHeader,
  Pagination,
  SelectField,
} from '@/shared/ui';
import { useGroups } from '../catalog';
import { fetchStudents, type ConsentStatus, type Student } from './api';
import { AddStudentModal } from './AddStudentModal';
import { studentLabel, studentUid } from './display';
import { RevokeModal } from './RevokeModal';

const PAGE_SIZE = 10;

function actUrl(student: Student): string {
  const document = encodeURIComponent(student.revocation_document ?? '');
  return `/students/${student.id}/act?doc=${document}&date=${student.revocation_date ?? ''}`;
}

function StudentRow({ student, onRevoke }: { student: Student; onRevoke: () => void }) {
  const revoked = student.consent_status === 'revoked';
  return (
    <tr>
      <td>{studentLabel(student)}</td>
      <td>{student.group_name}</td>
      <td>{studentUid(student)}</td>
      <td>{student.consent_document}</td>
      <td>{formatDate(student.consent_date)}</td>
      <td>
        <Badge tone={revoked ? 'neutral' : 'success'}>{revoked ? 'Отозвано' : 'Действует'}</Badge>
      </td>
      <td className="actions">
        {revoked ? (
          <Link to={actUrl(student)} className="btn btn--primary btn--small">
            Сформировать акт
          </Link>
        ) : (
          <Button variant="secondary" className="btn--small" onClick={onRevoke}>
            Отозвать
          </Button>
        )}
      </td>
    </tr>
  );
}

export function StudentsPage() {
  const [groupId, setGroupId] = useState('');
  const [status, setStatus] = useState<ConsentStatus | ''>('');
  const [page, setPage] = useState(1);
  const [adding, setAdding] = useState(false);
  const [revoking, setRevoking] = useState<Student | null>(null);
  const groups = useGroups();
  const [params, setParams] = useSearchParams();
  const studentId = params.get('id') ?? '';
  const size = studentId ? 100 : PAGE_SIZE;

  const students = useRequest(
    () =>
      fetchStudents({
        page,
        size,
        group_id: groupId ? Number(groupId) : undefined,
        consent_status: status || undefined,
      }),
    `students:${page}:${size}:${groupId}:${status}`,
  );
  const items = (students.data?.items ?? []).filter(
    (s) => !studentId || String(s.id) === studentId,
  );

  return (
    <>
      <PageHeader
        title="Студенты"
        subtitle="Список студентов, согласия и отзывы"
        actions={<Button onClick={() => setAdding(true)}>Добавить студента</Button>}
      />
      {studentId && (
        <FilterChip
          text={`Студент №${studentId}`}
          onClear={() => setParams(new URLSearchParams())}
        />
      )}
      <div className="toolbar">
        <SelectField
          label="Группа"
          value={groupId}
          onChange={(event) => {
            setGroupId(event.target.value);
            setPage(1);
          }}
        >
          <option value="">Все группы</option>
          {(groups.data ?? []).map((group) => (
            <option key={group.id} value={group.id}>
              {group.name}
            </option>
          ))}
        </SelectField>
        <SelectField
          label="Статус согласия"
          value={status}
          onChange={(event) => {
            setStatus(event.target.value as ConsentStatus | '');
            setPage(1);
          }}
        >
          <option value="">Все</option>
          <option value="active">Действует</option>
          <option value="revoked">Отозвано</option>
        </SelectField>
      </div>

      <DataState
        loading={students.loading}
        error={students.error}
        empty={items.length === 0}
        emptyText="Студентов не найдено"
        onRetry={students.reload}
      >
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>ФИО</th>
                <th>Группа</th>
                <th>UID</th>
                <th>№ согласия</th>
                <th>Дата согласия</th>
                <th>Статус</th>
                <th className="actions">Действие</th>
              </tr>
            </thead>
            <tbody>
              {items.map((student) => (
                <StudentRow
                  key={student.id}
                  student={student}
                  onRevoke={() => setRevoking(student)}
                />
              ))}
            </tbody>
          </table>
          <Pagination
            page={page}
            size={size}
            total={studentId ? items.length : (students.data?.total ?? 0)}
            onChange={setPage}
          />
        </div>
      </DataState>

      {adding && (
        <AddStudentModal
          groups={groups.data ?? []}
          onClose={() => setAdding(false)}
          onCreated={() => {
            setAdding(false);
            students.reload();
          }}
        />
      )}
      {revoking && (
        <RevokeModal
          student={revoking}
          onClose={() => setRevoking(null)}
          onRevoked={() => {
            setRevoking(null);
            students.reload();
          }}
        />
      )}
    </>
  );
}