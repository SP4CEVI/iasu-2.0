from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import require_admin
from app.models import Admin, Card, Group, Pair, Schedule
from app.responses import ok

router = APIRouter(tags=["admin-catalog"])


@router.get("/v1/admin/groups")
def list_groups(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    rows = db.query(Group).order_by(Group.name).all()
    return ok([{"id": g.id, "name": g.name} for g in rows])


@router.get("/v1/admin/schedules")
def list_schedules(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    rows = (
        db.query(Schedule)
        .order_by(Schedule.academic_year, Schedule.semester, Schedule.pair_number)
        .all()
    )
    return ok(
        [
            {
                "id": s.id,
                "academic_year": s.academic_year,
                "semester": s.semester,
                "pair_number": s.pair_number,
                "course": s.course,
                "lesson_type": s.lesson_type,
                "start_time": s.start_time.strftime("%H:%M"),
                "end_time": s.end_time.strftime("%H:%M"),
            }
            for s in rows
        ]
    )


@router.get("/v1/admin/pairs")
def list_pairs(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    rows = (
        db.query(Pair)
        .options(joinedload(Pair.schedule), joinedload(Pair.pps), joinedload(Pair.group))
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
                "date_from": p.date_from.isoformat(),
                "date_to": p.date_to.isoformat(),
                "pps_id": p.pps_id,
                "pps_name": p.pps.display_name if p.pps else None,
                "group_id": p.group_id,
                "group_name": p.group.name if p.group else None,
                "schedule_id": p.schedule_id,
                "active": p.active,
            }
            for p in rows
        ]
    )


@router.get("/v1/admin/cards")
def list_cards(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    rows = db.query(Card).order_by(Card.id).all()
    return ok(
        [
            {
                "id": c.id,
                "uid": c.uid,
                "student_id": c.student_id,
                "active": c.active,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in rows
        ]
    )
