from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Student, EventLog
from app.schemas_security import StudentCreate, ConsentRevocation

class SecurityService:
    def __init__(self, db: Session):
        self.db = db

    def _log_event(self, event_type: str, severity: str, meta: dict):
        """Внутренний метод для записи в event_log"""
        event = EventLog(
            event_type=event_type,
            severity=severity,
            meta=meta,
            timestamp=datetime.now(timezone.utc)
        )
        self.db.add(event)
        self.db.commit()

    def add_student(self, student_in: StudentCreate) -> Student:
        #Добавляет студента с согласием. Если нет обязательных полей — логирует ошибку
        if not student_in.consent_document or not student_in.consent_date:
            self._log_event(
                event_type="student_consent_missing",
                severity="warning",
                meta={"uid": student_in.uid, "reason": "missing consent fields"}
            )
            raise ValueError("Отсутствуют обязательные поля согласия (номер или дата)")

        # Проверка на дубликат UID
        existing = self.db.query(Student).filter(Student.uid == student_in.uid).first()
        if existing:
            raise ValueError(f"Студент с UID {student_in.uid} уже существует")

        student = Student(
            full_name=student_in.full_name,
            uid=student_in.uid,
            group_id=student_in.group_id,
            consent_document=student_in.consent_document,
            consent_date=student_in.consent_date,
        )
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)

        self._log_event(
            event_type="consent_granted",
            severity="info",
            meta={"student_id": student.id, "uid": student.uid, "consent_document": student.consent_document}
        )
        return student

    def revoke_consent(self, student_id: int, revocation: ConsentRevocation) -> Student:
        #Отзывает согласие и обезличивает данные
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Студент с ID {student_id} не найден")
        
        if student.anonymized_at:
            raise ValueError("Согласие уже было отозвано ранее")

        if not revocation.revocation_document:
            self._log_event(
                event_type="revoke_without_document",
                severity="warning",
                meta={"student_id": student_id}
            )
            raise ValueError("Для отзыва согласия необходим номер заявления")

        # Зануление персональных данных
        student.full_name = None
        student.uid = None
        student.revocation_document = revocation.revocation_document
        student.revocation_date = revocation.revocation_date
        student.anonymized_at = datetime.now(timezone.utc)

        self._log_event(
            event_type="consent_revoked",
            severity="info",
            meta={
                "student_id": student.id,
                "revocation_document": revocation.revocation_document
            }
        )
        
        self.db.commit()
        self.db.refresh(student)
        return student

    def check_attendance_consent(self, student_id: int) -> dict:
        #Проверка перед отметкой посещаемости
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return {"allowed": False, "status": 404, "reason": "unknown_uid"}
        
        if student.anonymized_at:
            self._log_event(
                event_type="consent_revoked",
                severity="info",
                meta={"student_id": student_id, "action": "attendance_check_blocked"}
            )
            return {"allowed": False, "status": 403, "reason": "consent_revoked"}
            
        return {"allowed": True, "status": 200}

    def get_event_log(self, severity: Optional[str] = None, event_type: Optional[str] = None, page: int = 1, size: int = 50) -> dict:
        #Получение журнала событий
        size = min(size, 200)
        offset = (page - 1) * size

        query = self.db.query(EventLog)
        count_query = self.db.query(func.count(EventLog.id))

        if severity:
            query = query.filter(EventLog.severity == severity)
            count_query = count_query.filter(EventLog.severity == severity)
        if event_type:
            query = query.filter(EventLog.event_type == event_type)
            count_query = count_query.filter(EventLog.event_type == event_type)

        total = count_query.scalar()
        items = query.order_by(EventLog.timestamp.desc()).offset(offset).limit(size).all()

        return {
            "items": [
                {
                    "id": item.id,
                    "event_type": item.event_type,
                    "severity": item.severity,
                    "meta": item.meta,
                    "timestamp": item.timestamp.isoformat()
                }
                for item in items
            ],
            "total": total,
            "page": page,
            "size": size
        }