"""
NetSage AI — Custom Exception Hierarchy.
"""
from __future__ import annotations

from typing import Any, Optional


class NetSageException(Exception):
    """Base exception for all NetSage AI errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}
        if error_code:
            self.error_code = error_code


# ---------------------------------------------------------------------------
# 404 Errors
# ---------------------------------------------------------------------------

class CaseNotFoundError(NetSageException):
    status_code = 404
    error_code = "CASE_NOT_FOUND"


class DiagnosisNotFoundError(NetSageException):
    status_code = 404
    error_code = "DIAGNOSIS_NOT_FOUND"


class ReviewNotFoundError(NetSageException):
    status_code = 404
    error_code = "REVIEW_NOT_FOUND"


class VerificationNotFoundError(NetSageException):
    status_code = 404
    error_code = "VERIFICATION_NOT_FOUND"


# ---------------------------------------------------------------------------
# 400 / 422 Errors
# ---------------------------------------------------------------------------

class DuplicateCaseError(NetSageException):
    status_code = 409
    error_code = "DUPLICATE_CASE"


class InvalidWorkflowTransitionError(NetSageException):
    status_code = 400
    error_code = "INVALID_WORKFLOW_TRANSITION"


class InvalidReviewStateError(NetSageException):
    status_code = 400
    error_code = "INVALID_REVIEW_STATE"


class ValidationError(NetSageException):
    status_code = 422
    error_code = "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# AI Errors
# ---------------------------------------------------------------------------

class AIProviderError(NetSageException):
    status_code = 502
    error_code = "AI_PROVIDER_ERROR"


class AIResponseParseError(NetSageException):
    status_code = 502
    error_code = "AI_RESPONSE_PARSE_ERROR"


class AIResponseValidationError(NetSageException):
    status_code = 502
    error_code = "AI_RESPONSE_VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# Parser Errors
# ---------------------------------------------------------------------------

class UnsupportedParserFormatError(NetSageException):
    status_code = 422
    error_code = "UNSUPPORTED_PARSER_FORMAT"


# ---------------------------------------------------------------------------
# Database Errors
# ---------------------------------------------------------------------------

class DatabaseError(NetSageException):
    status_code = 503
    error_code = "DATABASE_ERROR"
