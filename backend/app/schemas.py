from datetime import date, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class OkResponse(BaseModel, Generic[T]):
    status: str = "ok"
    data: T


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str


class EnrollRequest(BaseModel):
    code: str
    device_id: str
    public_key: str


class AttendanceRequest(BaseModel):
    uid: str
    pair_id: int
    group_id: int
    event_type: str = Field(pattern="^(check_in|check_out)$")
    timestamp: datetime


class AdminLoginRequest(BaseModel):
    login: str
    password: str


class AdminChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class StudentCreateRequest(BaseModel):
    uid: str
    group_id: int
    consent_document: str
    consent_date: date


class StudentRevokeRequest(BaseModel):
    revocation_document: str
    revocation_date: date


class EnrollmentCodeCreateRequest(BaseModel):
    teacher_id: int
    expires_in_hours: int = 24


class PageMeta(BaseModel):
    items: list[Any]
    total: int
    page: int
    size: int
