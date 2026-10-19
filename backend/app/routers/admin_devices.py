import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import ApiError, require_admin
from app.models import Admin, Device, EnrollmentCode, Teacher
from app.responses import ok
from app.schemas import EnrollmentCodeCreateRequest

router = APIRouter(tags=["admin-devices"])


@router.post("/v1/admin/enrollment-codes")
def create_enrollment_code(
    payload: EnrollmentCodeCreateRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin),
):
    teacher = db.query(Teacher).filter(Teacher.id == payload.teacher_id, Teacher.active.is_(True)).first()
    if teacher is None:
        raise ApiError("Преподаватель не найден", 404)
    code = secrets.token_hex(4).upper()
    code = f"{code[:4]}-{code[4:]}"
    while db.query(EnrollmentCode).filter(EnrollmentCode.code == code).first():
        code = secrets.token_hex(4).upper()
        code = f"{code[:4]}-{code[4:]}"

    expires_at = datetime.now(timezone.utc) + timedelta(hours=payload.expires_in_hours)
    row = EnrollmentCode(
        code=code,
        teacher_id=payload.teacher_id,
        created_by_admin=admin.id,
        expires_at=expires_at,
    )
    db.add(row)
    db.commit()
    return ok(
        {
            "code": code,
            "teacher_id": payload.teacher_id,
            "teacher_name": teacher.display_name,
            "expires_at": expires_at.isoformat(),
        }
    )


@router.get("/v1/admin/devices")
def list_devices(
    teacher_id: int | None = None,
    active: bool | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin),
):
    q = db.query(Device)
    if teacher_id is not None:
        q = q.filter(Device.teacher_id == teacher_id)
    if active is not None:
        q = q.filter(Device.active.is_(active))
    total = q.count()
    rows = q.order_by(Device.created_at.desc()).offset((page - 1) * size).limit(size).all()
    teachers = {
        t.id: t.display_name
        for t in db.query(Teacher).filter(Teacher.id.in_({d.teacher_id for d in rows} or {-1})).all()
    }
    return ok(
        {
            "items": [
                {
                    "id": d.id,
                    "teacher_id": d.teacher_id,
                    "teacher_name": teachers.get(d.teacher_id),
                    "active": d.active,
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                }
                for d in rows
            ],
            "total": total,
            "page": page,
            "size": size,
        }
    )


@router.post("/v1/admin/devices/{device_id}/revoke")
def revoke_device(
    device_id: str,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin),
):
    device = db.query(Device).filter(Device.id == device_id).first()
    if device is None:
        raise ApiError("Устройство не найдено", 404)
    device.active = False
    db.commit()
    return ok({"id": device.id, "active": False})


@router.get("/v1/admin/teachers")
def list_teachers(
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin),
):
    rows = (
        db.query(Teacher)
        .filter(Teacher.active.is_(True))
        .order_by(Teacher.last_name, Teacher.first_name)
        .all()
    )
    return ok(
        [
            {
                "id": t.id,
                "last_name": t.last_name,
                "first_name": t.first_name,
                "middle_name": t.middle_name,
                "uid": t.uid,
                "full_name": t.display_name,
            }
            for t in rows
        ]
    )
