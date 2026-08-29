"""
NetSage AI — FastAPI Application Entry Point.

Start with: uvicorn app.main:app --reload
"""
from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.database import Base, create_all_tables, engine
from app.core.exceptions import NetSageException
from app.core.logging_config import configure_logging, get_logger

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger("app.main")


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    # Check and warn about production defaults
    settings.warn_production_defaults()

    # Create all tables (Alembic handles migrations in production)
    from app.models import _import_all_models
    _import_all_models()
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created.")
    logger.info("%s v%s started (%s mode)", settings.app_name, settings.app_version, settings.environment)

    yield

    logger.info("%s shutting down.", settings.app_name)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-assisted Cisco network troubleshooting system. "
        "Combines deterministic rule checks with AI analysis. "
        "Human review is mandatory before any diagnosis becomes final. "
        "The AI is an assistant — it does not autonomously configure networks."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# HTTP Security & Timing Middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def security_and_timing_middleware(request: Request, call_next):
    # 1. Request Body Size Protection
    content_length = request.headers.get("content-length")
    max_bytes = settings.max_request_body_mb * 1024 * 1024
    if content_length and int(content_length) > max_bytes:
        return JSONResponse(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            content={
                "error": {
                    "code": "REQUEST_ENTITY_TOO_LARGE",
                    "message": f"Request body exceeds maximum allowed size of {settings.max_request_body_mb}MB.",
                }
            },
        )

    # 2. Request ID & Timing
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = str(duration_ms)

    logger.info(
        "HTTP %s %s | Status: %d | Duration: %.2fms | Request-ID: %s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )
    return response


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------

@app.exception_handler(NetSageException)
async def netsage_exception_handler(request: Request, exc: NetSageException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    import logging
    logging.getLogger(__name__).error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred.",
                "details": {},
            }
        },
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

from app.api.routes.health import router as health_router
from app.api.routes.cases import router as cases_router
from app.api.routes.evidence import router as evidence_router
from app.api.routes.diagnosis import router as diagnosis_router
from app.api.routes.rules import router as rules_router
from app.api.routes.reviews import router as reviews_router
from app.api.routes.verification import router as verification_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.responsible_ai import router as responsible_ai_router
from app.api.routes.evaluation import router as evaluation_router
from app.api.routes.audit import router as audit_router

API_PREFIX = "/api/v1"

app.include_router(health_router)
app.include_router(cases_router, prefix=API_PREFIX)
app.include_router(evidence_router, prefix=API_PREFIX)
app.include_router(diagnosis_router, prefix=API_PREFIX)
app.include_router(rules_router, prefix=API_PREFIX)
app.include_router(reviews_router, prefix=API_PREFIX)
app.include_router(verification_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)
app.include_router(responsible_ai_router, prefix=API_PREFIX)
app.include_router(evaluation_router, prefix=API_PREFIX)
app.include_router(audit_router, prefix=API_PREFIX)


@app.get("/", include_in_schema=False)
def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
    }


@app.get("/ready", tags=["Health"], summary="Readiness check")
def readiness_check():
    from app.core.database import check_database_connection
    db_ok = check_database_connection()
    if not db_ok:
        return JSONResponse(status_code=503, content={"status": "not_ready", "reason": "database_unavailable"})
    return {"status": "ready", "service": settings.app_name}
