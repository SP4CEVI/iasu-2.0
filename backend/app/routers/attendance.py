from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.crypto import normalize_uid
from app.database import get_db
from app.deps import ApiError, require_device
from app.models import Attendance, Card, Device, Pair
from app.responses import ok
from app.schemas import AttendanceRequest
from app.services.event_log import log_event

router = APIRouter(tags=["attendance"])


@router.post("/v1/attendance")
def mark_attendance(
    payload: AttendanceRequest,
    db: Session = Depends(get_db),
    device: Device = Depends(require_device),
):
    uid = normalize_uid(payload.uid)

    pair = (
        db.query(Pair)
        .filter(
            Pair.id == payload.pair_id,
            Pair.pps_id == device.teacher_id,
            Pair.group_id == payload.group_id,
            Pair.active.is_(True),
        )
        .first()
    )
    if pair is None:
        log_event(
            db,
            "no_pair",
            "error",
            {
                "device_id": device.id,
                "teacher_id": device.teacher_id,
                "pair_id": payload.pair_id,
                "group_id": payload.group_id,
            },
            commit=True,
        )
        raise ApiError("Нет доступа к паре для этой группы", 403)

    card = (
        db.query(Card)
        .options(joinedload(Card.student))
        .filter(Card.uid == uid, Card.active.is_(True))
        .first()
    )
    if card is None:
        log_event(
            db,
            "unknown_uid",
            "warning",
            {
                "device_id": device.id,
                "uid": uid,
                "pair_id": payload.pair_id,
                "group_id": payload.group_id,
            },
            commit=True,
        )
        raise ApiError("Карта не найдена", 404)

    student = card.student
    if student.anonymized_at is not None:
        log_event(
            db,
            "consent_revoked",
            "info",
            {
                "device_id": device.id,
                "uid": uid,
                "student_id": student.id,
                "teacher_id": device.teacher_id,
            },
            commit=True,
        )
        raise ApiError("Согласие отозвано", 403)

    if student.group_id != payload.group_id:
        log_event(
            db,
            "student_wrong_group",
            "warning",
            {
                "device_id": device.id,
                "uid": uid,
                "student_id": student.id,
                "group_id": payload.group_id,
                "student_group_id": student.group_id,
            },
            commit=True,
        )
        raise ApiError("Студент не из выбранной группы", 400)

    event_ts = payload.timestamp
    if event_ts.tzinfo is None:
        event_ts = event_ts.replace(tzinfo=timezone.utc)

    day_start = event_ts.replace(hour=0, minute=0, second=0, microsecond=0)
    day_events = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student.id,
            Attendance.pair_id == pair.id,
            Attendance.timestamp >= day_start,
            Attendance.timestamp <= event_ts,
        )
        .order_by(Attendance.timestamp)
        .all()
    )

    last = day_events[-1] if day_events else None
    if payload.event_type == "check_in" and last and last.event_type == "check_in":
        log_event(
            db,
            "duplicate_check_in",
            "info",
            {
                "device_id": device.id,
                "uid": uid,
                "student_id": student.id,
                "pair_id": payload.pair_id,
                "group_id": payload.group_id,
            },
            commit=True,
        )
        raise ApiError("Повторный check_in без check_out", 400)

    if payload.event_type == "check_out" and (last is None or last.event_type != "check_in"):
        log_event(
            db,
            "check_out_without_in",
            "warning",
            {
                "device_id": device.id,
                "uid": uid,
                "student_id": student.id,
                "pair_id": payload.pair_id,
                "group_id": payload.group_id,
            },
            commit=True,
        )
        raise ApiError("check_out без check_in", 400)

    record = Attendance(
        student_id=student.id,
        pair_id=pair.id,
        device_id=device.id,
        event_type=payload.event_type,
        timestamp=event_ts,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return ok(
        {
            "id": record.id,
            "student_id": student.id,
            "card_id": card.id,
            "event_type": record.event_type,
            "timestamp": record.timestamp.isoformat(),
        }
    )
