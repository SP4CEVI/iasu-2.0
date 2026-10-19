from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Admin, EventLog
from app.responses import ok

router = APIRouter(tags=["admin-events"])


@router.get("/v1/admin/event-log")
def list_events(
    severity: str | None = None,
    event_type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    meta_device_id: str | None = Query(default=None, alias="meta.device_id"),
    meta_uid: str | None = Query(default=None, alias="meta.uid"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin),
):
    q = db.query(EventLog)
    if severity:
        q = q.filter(EventLog.severity == severity)
    if event_type:
        q = q.filter(EventLog.event_type == event_type)
    if date_from:
        q = q.filter(
            EventLog.timestamp >= datetime.combine(date_from, time.min, tzinfo=timezone.utc)
        )
    if date_to:
        q = q.filter(
            EventLog.timestamp <= datetime.combine(date_to, time.max, tzinfo=timezone.utc)
        )
    if meta_device_id:
        q = q.filter(EventLog.meta["device_id"].astext == meta_device_id)
    if meta_uid:
        q = q.filter(EventLog.meta["uid"].astext == meta_uid)

    total = q.count()
    rows = q.order_by(EventLog.timestamp.desc()).offset((page - 1) * size).limit(size).all()
    return ok(
        {
            "items": [
                {
                    "id": e.id,
                    "event_type": e.event_type,
                    "severity": e.severity,
                    "meta": e.meta,
                    "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                }
                for e in rows
            ],
            "total": total,
            "page": page,
            "size": size,
        }
    )
