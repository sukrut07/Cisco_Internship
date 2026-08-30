"""
NetSage AI — API Dependency Injection Helpers.
"""
from __future__ import annotations

import logging
from typing import Generator, Optional

from fastapi import Depends, Header, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def verify_api_key(
    x_api_key: Optional[str] = Security(api_key_header_scheme),
    bearer_auth: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> Optional[str]:
    """
    Verify API key when REQUIRE_AUTH=true in settings.

    Accepts key via 'X-API-Key' header or 'Authorization: Bearer <key>'.
    When REQUIRE_AUTH=false (default in development), permits all requests.
    """
    settings = get_settings()
    if not settings.require_auth:
        return "development-anonymous"

    configured_key = settings.api_key or settings.secret_key
    provided_key = x_api_key or (bearer_auth.credentials if bearer_auth else None)

    if not provided_key or provided_key != configured_key:
        logger.warning("Unauthorized access attempt — invalid or missing API key.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid or missing API key."},
            headers={"WWW-Authenticate": "Bearer"},
        )

    return provided_key


def get_settings_dependency():
    """Dependency that returns application settings."""
    return get_settings()


def get_current_user_or_anonymous(
    api_key: Optional[str] = Depends(verify_api_key),
) -> str:
    """Return identity of the current user/actor (or 'anonymous'/'api')."""
    return api_key or "anonymous"
