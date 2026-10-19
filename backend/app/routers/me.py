from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import ApiError, require_device
from app.models import Attendance, Device, Group, Pair
from app.responses import ok

router = APIRouter(tags=["me"])


@router.get("/v1/me/pairs")
def my_pairs(
    db: Session = Depends(get_db),
    device: Device = Depends(require_device),
):
    rows = (
        db.query(Pair)
        .options(joinedload(Pair.schedule), joinedload(Pair.group))
        .filter(
            Pair.pps_id == device.teacher_id,
            Pair.active.is_(True),
        )
        .order_by(Pair.name)
        .all()
    )
    return ok(
        [
            {
                "id": p.id,
                "name": p.name,
                "room": p.room,
                "periodicity": p.periodicity,
                "group_id": p.group_id,
                "group_name": p.group.name if p.group else None,
                "schedule": {
                    "id": p.schedule.id,
                    "academic_year": p.schedule.academic_year,
                    "semester": p.schedule.semester,
                    "pair_number": p.schedule.pair_number,
                    "course": p.schedule.course,
                    "lesson_type": p.schedule.lesson_type,
                    "start_time": p.schedule.start_time.strftime("%H:%M"),
                    "end_time": p.schedule.end_time.strftime("%H:%M"),
                }
                if p.schedule
                else None,
            }
            for p in rows
        ]
    )


@router.get("/v1/me/groups")
def my_groups(
    pair_id: int = Query(...),
    db: Session = Depends(get_db),
    device: Device = Depends(require_device),
):
    rows = (
        db.query(Group)
        .join(Pair, Pair.group_id == Group.id)
        .filter(
            Pair.pps_id == device.teacher_id,
            Pair.id == pair_id,
            Pair.active.is_(True),
        )
        .distinct()
        .order_by(Group.name)
        .all()
    )
    return ok([{"id": g.id, "name": g.name} for g in rows])


@router.get("/v1/me/attendance")
def my_attendance(
    pair_id: int = Query(...),
    group_id: int = Query(...),
    date_str: date = Query(..., alias="date"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    device: Device = Depends(require_device),
):
    pair = (
        db.query(Pair)
        .options(joinedload(Pair.group), joinedload(Pair.schedule))
        .filter(
            Pair.id == pair_id,
            Pair.pps_id == device.teacher_id,
            Pair.group_id == group_id,
            Pair.active.is_(True),
        )
        .first()
    )
    if pair is None:
        raise ApiError("Нет доступа к паре и группе", 403)

    day_start = datetime.combine(date_str, time.min, tzinfo=timezone.utc)
    day_end = datetime.combine(date_str, time.max, tzinfo=timezone.utc)

    events = (
        db.query(Attendance)
        .options(joinedload(Attendance.student))
        .filter(
            Attendance.pair_id == pair.id,
            Attendance.timestamp >= day_start,
            Attendance.timestamp <= day_end,
        )
        .order_by(Attendance.timestamp)
        .all()
    )

    by_student: dict[int, dict] = {}
    for ev in events:
        student = ev.student
        revoked = student.anonymized_at is not None
        entry = by_student.setdefault(
            student.id,
            {
                "student_id": student.id,
                "revoked": revoked,
                "check_in": None,
                "check_out": None,
            },
        )
        hhmm = ev.timestamp.astimezone(timezone.utc).strftime("%H:%M")
        if ev.event_type == "check_in" and entry["check_in"] is None:
            entry["check_in"] = hhmm
        elif ev.event_type == "check_out":
            entry["check_out"] = hhmm

    items = list(by_student.values())
    total = len(items)
    start = (page - 1) * size
    page_items = items[start : start + size]

    return ok(
        {
            "pair": pair.name,
            "group": pair.group.name,
            "date": date_str.isoformat(),
            "items": page_items,
            "total": total,
            "page": page,
            "size": size,
        }
    )
