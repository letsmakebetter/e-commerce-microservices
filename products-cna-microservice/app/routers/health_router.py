"""Liveness and readiness, in the shape every service of the platform uses."""

from __future__ import annotations

import time

from fastapi import APIRouter, Response
from sqlalchemy import text

from app.db.config import engine
from app.settings import settings

router = APIRouter(tags=["System"])

_STARTED_AT = time.monotonic()


async def _database_up() -> bool:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@router.get("/health")
async def health(response: Response) -> dict:
    database_ok = await _database_up()
    response.status_code = 200 if database_ok else 503

    return {
        "status": "ok" if database_ok else "degraded",
        "service": settings.service_name,
        "version": settings.version,
        "uptimeSeconds": round(time.monotonic() - _STARTED_AT),
        "dependencies": {"postgresql": "up" if database_ok else "down"},
    }


@router.get("/ready")
async def ready(response: Response) -> dict:
    database_ok = await _database_up()
    response.status_code = 200 if database_ok else 503
    return {"ready": database_ok}
