from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.deps import ApiError
from app.responses import err
from app.routers import (
    admin_auth,
    admin_catalog,
    admin_devices,
    admin_events,
    admin_students,
    attendance,
    enroll,
    me,
)

settings = get_settings()

app = FastAPI(title="Attendance API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ApiError)
async def api_error_handler(_request: Request, exc: ApiError):
    return err(exc.message, exc.status_code)


app.include_router(enroll.router)
app.include_router(me.router)
app.include_router(attendance.router)
app.include_router(admin_auth.router)
app.include_router(admin_students.router)
app.include_router(admin_devices.router)
app.include_router(admin_events.router)
app.include_router(admin_catalog.router)


@app.get("/health")
def health():
    return {"status": "ok"}
