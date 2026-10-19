from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.crypto import normalize_uid
from app.database import get_db
from app.deps import ApiError, require_admin
from app.models import Admin, Card, Student
from app.responses import ok
from app.schemas import StudentCreateRequest, StudentRevokeRequest
from app.services.event_log import log_event

router = APIRouter(tags=["admin-students"])


def _student_dict(s: Student) -> dict:
    consent_status = "revoked" if s.anonymized_at is not None else "active"
    cards = [
        {
            "id": c.id,
            "uid": c.uid,
            "active": c.active,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in (s.cards or [])
    ]
    return {
        "id": s.id,
        "group_id": s.group_id,
        "group_name": s.group.name if s.group else None,
        "cards": cards,
        "consent_document": s.consent_document,
        "consent_date": s.consent_date.isoformat() if s.consent_date else None,
        "revocation_document": s.revocation_document,
        "revocation_date": s.revocation_date.isoformat() if s.revocation_date else None,
        "anonymized_at": s.anonymized_at.isoformat() if s.anonymized_at else None,
        "consent_status": consent_status,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


@router.get("/v1/admin/students")
def list_students(
    group_id: int | None = None,
    consent_status: str | None = Query(default=None, pattern="^(active|revoked)$"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin),
):
    q = db.query(Student).options(joinedload(Student.group), joinedload(Student.cards))
    if group_id is not None:
        q = q.filter(Student.group_id == group_id)
    if consent_status == "active":
        q = q.filter(Student.anonymized_at.is_(None))
    elif consent_status == "revoked":
        q = q.filter(Student.anonymized_at.isnot(None))
    total = q.count()
    rows = q.order_by(Student.id).offset((page - 1) * size).limit(size).all()
    return ok(
        {
            "items": [_student_dict(s) for s in rows],
            "total": total,
            "page": page,
            "size": size,
        }
    )


@router.post("/v1/admin/students")
def create_student(
    payload: StudentCreateRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin),
):
    if not payload.uid or not payload.consent_document:
        log_event(
            db,
            "student_consent_missing",
            "warning",
            {"details": "missing required fields"},
            commit=True,
        )
        raise ApiError("Обязательные поля согласия не заполнены", 400)

    uid = normalize_uid(payload.uid)
    if db.query(Card).filter(Card.uid == uid).first():
        raise ApiError("Карта с таким UID уже существует", 400)

    student = Student(
        group_id=payload.group_id,
        consent_document=payload.consent_document.strip(),
        consent_date=payload.consent_date,
    )
    db.add(student)
    db.flush()
    db.add(Card(uid=uid, student_id=student.id, active=True))
    db.commit()
    student = (
        db.query(Student)
        .options(joinedload(Student.group), joinedload(Student.cards))
        .filter(Student.id == student.id)
        .first()
    )
    return ok(_student_dict(student))


@router.post("/v1/admin/students/{student_id}/revoke")
def revoke_student(
    student_id: int,
    payload: StudentRevokeRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin),
):
    student = (
        db.query(Student)
        .options(joinedload(Student.group), joinedload(Student.cards))
        .filter(Student.id == student_id)
        .first()
    )
    if student is None:
        raise ApiError("Студент не найден", 404)
    if not payload.revocation_document:
        log_event(
            db,
            "revoke_without_document",
            "warning",
            {"student_id": student_id},
            commit=True,
        )
        raise ApiError("Укажите номер заявления об отзыве", 400)
    if student.anonymized_at is not None:
        raise ApiError("Согласие уже отозвано", 400)

    old_uids = [c.uid for c in student.cards if c.uid]
    for card in student.cards:
        card.uid = None
        card.active = False
    student.revocation_document = payload.revocation_document.strip()
    student.revocation_date = payload.revocation_date
    student.anonymized_at = datetime.now(timezone.utc)
    log_event(
        db,
        "consent_revoked",
        "info",
        {"student_id": student.id, "uids": old_uids},
    )
    db.commit()
    db.refresh(student)
    return ok(_student_dict(student))
