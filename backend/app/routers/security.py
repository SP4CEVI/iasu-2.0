from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.security_service import SecurityService
from app.schemas_security import StudentCreate, ConsentRevocation, PaginatedResponse

router = APIRouter(prefix="/v1/admin", tags=["security"])

@router.post("/students", response_model=dict)
def create_student(student_in: StudentCreate, db: Session = Depends(get_db)):
    try:
        service = SecurityService(db)
        student = service.add_student(student_in)
        return {
            "status": "ok",
            "data": {
                "student_id": student.id,
                "full_name": student.full_name,
                "uid": student.uid
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/students/{student_id}/revoke", response_model=dict)
def revoke_student_consent(student_id: int, revocation: ConsentRevocation, db: Session = Depends(get_db)):
    try:
        service = SecurityService(db)
        student = service.revoke_consent(student_id, revocation)
        return {
            "status": "ok",
            "data": {
                "student_id": student.id,
                "anonymized_at": student.anonymized_at.isoformat() if student.anonymized_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/event-log", response_model=PaginatedResponse)
def get_event_log(
    severity: str = Query(None, description="info, warning, или error"),
    event_type: str = Query(None, description="Тип события, например unknown_uid"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    service = SecurityService(db)
    data = service.get_event_log(severity=severity, event_type=event_type, page=page, size=size)
    return {"status": "ok", "data": data}