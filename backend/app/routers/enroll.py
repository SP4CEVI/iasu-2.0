from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crypto import load_public_key, public_key_to_pem
from app.database import get_db
from app.deps import ApiError
from app.models import Device, EnrollmentCode
from app.responses import ok
from app.schemas import EnrollRequest
from app.services.event_log import log_event

router = APIRouter(tags=["enroll"])


@router.post("/v1/enroll")
def enroll(payload: EnrollRequest, db: Session = Depends(get_db)):
    code = db.query(EnrollmentCode).filter(EnrollmentCode.code == payload.code).first()
    if code is None:
        log_event(db, "enroll_code_invalid", "warning", {"code": payload.code}, commit=True)
        raise ApiError("Код регистрации не найден", 400)

    now = datetime.now(timezone.utc)
    expires = code.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)

    if code.used_at is not None:
        log_event(
            db,
            "enroll_code_used",
            "warning",
            {"code": payload.code, "device_id": payload.device_id},
            commit=True,
        )
        raise ApiError("Код уже использован", 400)

    if expires < now:
        log_event(
            db,
            "enroll_code_expired",
            "info",
            {"code": payload.code, "device_id": payload.device_id},
            commit=True,
        )
        raise ApiError("Код истёк", 400)

    existing = db.query(Device).filter(Device.id == payload.device_id).first()
    if existing is not None:
        log_event(
            db,
            "enroll_device_exists",
            "info",
            {"device_id": payload.device_id},
            commit=True,
        )
        raise ApiError("Устройство уже зарегистрировано", 400)

    try:
        key = load_public_key(payload.public_key)
        pem = public_key_to_pem(key)
    except Exception as exc:
        raise ApiError(f"Некорректный публичный ключ: {exc}", 400) from exc

    device = Device(
        id=payload.device_id,
        teacher_id=code.teacher_id,
        public_key=pem,
        active=True,
    )
    code.used_at = now
    db.add(device)
    db.commit()
    return ok({"device_id": device.id, "teacher_id": device.teacher_id})
