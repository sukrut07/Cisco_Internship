"""
NetSage AI — Security Utilities.

Provides basic input sanitization.
No API keys or secrets are ever logged.
No shell execution of user-provided commands.
"""
from __future__ import annotations

import re
import uuid


MAX_FIELD_LENGTH = 10_000  # characters
MAX_SHOW_OUTPUT_SIZE = 500_000  # bytes


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def sanitize_string(value: str, max_length: int = MAX_FIELD_LENGTH) -> str:
    """
    Strip leading/trailing whitespace and truncate to max_length.

    Does NOT execute or interpret the string.
    """
    if not isinstance(value, str):
        raise TypeError(f"Expected str, got {type(value)}")
    return value.strip()[:max_length]


def normalize_command_name(cmd: str) -> str:
    """
    Normalize a Cisco show-command name for consistent dictionary keys.

    Example: 'SHOW IP ROUTE' → 'show ip route'
    """
    return re.sub(r"\s+", " ", cmd.strip().lower())


def is_safe_case_id(case_id: str) -> bool:
    """Validate that a case_id matches expected format (e.g., CASE-001)."""
    return bool(re.match(r"^[A-Z0-9\-_]{1,50}$", case_id))


def redact_secrets(data: dict) -> dict:
    """
    Return a copy of a dict with sensitive keys redacted.
    Used to prevent secrets leaking into logs.
    """
    sensitive_keys = {"api_key", "ai_api_key", "secret_key", "password", "token"}
    return {
        k: "***REDACTED***" if k.lower() in sensitive_keys else v
        for k, v in data.items()
    }
