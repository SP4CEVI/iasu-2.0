from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List, Any

class StudentCreate(BaseModel):
    full_name: str
    uid: str
    group_id: int
    consent_document: str
    consent_date: date

class ConsentRevocation(BaseModel):
    revocation_document: str
    revocation_date: date

class EventLogItem(BaseModel):
    id: int
    event_type: str
    severity: str
    meta: dict
    timestamp: datetime

class PaginatedResponse(BaseModel):
    status: str = "ok"
    data: dict  # Будет содержать items, total, page, size