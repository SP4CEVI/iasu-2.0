from typing import Any

from fastapi.responses import JSONResponse


def ok(data: Any = None, status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"status": "ok", "data": data})


def err(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"status": "error", "message": message})
