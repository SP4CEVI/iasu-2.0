from datetime import datetime, timezone

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.crypto import build_signed_payload, verify_ecdsa_sha256
from app.database import get_db
from app.models import Admin, Device
from app.services.auth_admin import decode_token
from app.services.event_log import log_event

security = HTTPBearer(auto_error=False)
settings = get_settings()


class ApiError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


async def _read_body(request: Request) -> bytes:
    if hasattr(request.state, "raw_body"):
        return request.state.raw_body
    body = await request.body()
    request.state.raw_body = body
    return body


async def require_device(
    request: Request,
    db: Session = Depends(get_db),
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
    x_timestamp: str | None = Header(default=None, alias="X-Timestamp"),
    x_signature: str | None = Header(default=None, alias="X-Signature"),
) -> Device:
    if not x_device_id or not x_timestamp or not x_signature:
        log_event(
            db,
            "unknown_device",
            "error",
            {"reason": "missing_auth_headers"},
            commit=True,
        )
        raise ApiError("Требуется аутентификация устройства", 401)

    device = db.query(Device).filter(Device.id == x_device_id).first()
    if device is None:
        log_event(db, "unknown_device", "error", {"device_id": x_device_id}, commit=True)
        raise ApiError("Устройство не найдено", 401)

    if not device.active:
        log_event(db, "device_revoked", "warning", {"device_id": x_device_id}, commit=True)
        raise ApiError("Устройство отозвано", 403)

    try:
        ts = datetime.fromisoformat(x_timestamp.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
    except ValueError:
        log_event(
            db,
            "expired_timestamp",
            "warning",
            {"device_id": x_device_id, "reason": "invalid_timestamp"},
            commit=True,
        )
        raise ApiError("Некорректный timestamp", 401)

    age = abs((datetime.now(timezone.utc) - ts).total_seconds())
    if age > settings.signature_max_age_seconds:
        log_event(
            db,
            "expired_timestamp",
            "warning",
            {"device_id": x_device_id, "age_seconds": age},
            commit=True,
        )
        raise ApiError("Timestamp устарел", 401)

    body = await _read_body(request)
    body_str = body.decode("utf-8") if body else ""
    path = request.url.path
    if request.url.query:
        path = f"{path}?{request.url.query}"
    payload = build_signed_payload(request.method, path, body_str, x_timestamp)

    if not verify_ecdsa_sha256(device.public_key, payload, x_signature):
        log_event(
            db,
            "invalid_signature",
            "error",
            {"device_id": x_device_id, "reason": "signature mismatch"},
            commit=True,
        )
        raise ApiError("Невалидная подпись", 401)

    return device


def require_admin(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> Admin:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError("Требуется аутентификация", 401)
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise ApiError("Невалидный токен", 401)
    admin = db.query(Admin).filter(Admin.id == int(payload["sub"])).first()
    if admin is None or not admin.active:
        raise ApiError("Админ не найден или неактивен", 401)
    return admin
