"""
NetSage AI — Health Check Route.
"""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import check_database_connection
from app.ai.provider import get_provider_name

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Health check",
    description="Returns service health status including database and AI provider connectivity.",
)
async def health_check():
    settings = get_settings()
    db_ok = check_database_connection()

    status = "healthy" if db_ok else "degraded"
    http_code = 200 if db_ok else 503

    return JSONResponse(
        status_code=http_code,
        content={
            "status": status,
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "database": "connected" if db_ok else "unavailable",
            "ai_provider": get_provider_name(),
        },
    )
