"""
NetSage AI — Common Pydantic schemas (pagination, errors, metadata).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response wrapper."""

    items: List[T]
    page: int
    page_size: int
    total: int
    pages: int


class ErrorDetail(BaseModel):
    """Standard error response body."""

    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Envelope for error responses."""

    error: ErrorDetail


class APIMetadata(BaseModel):
    """Common metadata attached to responses."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    workflow_state: Optional[str] = None
