"""
NetSage AI — FastAPI Application Entry Point.

Start with: uvicorn app.main:app --reload
"""
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.database import Base, create_all_tables, engine
from app.core.exceptions import NetSageException
from app.core.logging_config import configure_logging

settings = get_settings()
configure_logging(settings.log_level)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    import logging
    logger = logging.getLogger(__name__)

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
# Request ID Middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
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
from app.api.routes.diagnosis import router as diagnosis_router
from app.api.routes.rules import router as rules_router
from app.api.routes.reviews import router as reviews_router
from app.api.routes.verification import router as verification_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.responsible_ai import router as responsible_ai_router
from app.api.routes.evaluation import router as evaluation_router

API_PREFIX = "/api/v1"

app.include_router(health_router)
app.include_router(cases_router, prefix=API_PREFIX)
app.include_router(diagnosis_router, prefix=API_PREFIX)
app.include_router(rules_router, prefix=API_PREFIX)
app.include_router(reviews_router, prefix=API_PREFIX)
app.include_router(verification_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)
app.include_router(responsible_ai_router, prefix=API_PREFIX)
app.include_router(evaluation_router, prefix=API_PREFIX)


@app.get("/", include_in_schema=False)
def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
