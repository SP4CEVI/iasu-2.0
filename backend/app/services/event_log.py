from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models import EventLog


def log_event(
    db: Session,
    event_type: str,
    severity: str,
    meta: dict[str, Any] | None = None,
    *,
    commit: bool = False,
) -> EventLog:
    entry = EventLog(
        event_type=event_type,
        severity=severity,
        meta=meta or {},
        timestamp=datetime.now(timezone.utc),
    )
    db.add(entry)
    if commit:
        db.commit()
        db.refresh(entry)
    else:
        db.flush()
    return entry
