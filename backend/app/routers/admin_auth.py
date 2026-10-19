from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import ApiError, require_admin
from app.models import Admin
from app.responses import ok
from app.schemas import AdminChangePasswordRequest, AdminLoginRequest
from app.services.auth_admin import (
    create_access_token,
    get_admin_by_login,
    hash_password,
    verify_password,
)
from app.services.event_log import log_event

router = APIRouter(tags=["admin-auth"])
settings = get_settings()


@router.post("/v1/admin/login")
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = get_admin_by_login(db, payload.login)
    if admin is None or not admin.active or not verify_password(payload.password, admin.password_hash):
        log_event(
            db,
            "admin_login_failed",
            "warning",
            {"login": payload.login, "reason": "wrong_password"},
            commit=True,
        )
        raise ApiError("Неверный логин или пароль", 401)
    token = create_access_token(admin.id, admin.login)
    return ok({"access_token": token, "token_type": "bearer", "login": admin.login})


@router.post("/v1/admin/change-password")
def change_password(
    payload: AdminChangePasswordRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin),
):
    if not verify_password(payload.current_password, admin.password_hash):
        raise ApiError("Неверный текущий пароль", 400)
    if len(payload.new_password) < 8:
        raise ApiError("Новый пароль должен быть не короче 8 символов", 400)
    admin.password_hash = hash_password(payload.new_password)
    db.commit()
    return ok({"changed": True})


@router.get("/v1/admin/meta")
def admin_meta(admin: Admin = Depends(require_admin)):
    return ok(
        {
            "login": admin.login,
            "apk_download_url": settings.apk_download_url,
        }
    )
