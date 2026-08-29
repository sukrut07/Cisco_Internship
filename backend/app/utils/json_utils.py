"""
NetSage AI — JSON Utilities.

Safe JSON parsing that never raises on bad input.
"""
from __future__ import annotations

import json
import re
from typing import Any, Optional


def safe_parse_json(text: str) -> Optional[dict | list]:
    """
    Attempt to parse a JSON string.
    Returns None on failure instead of raising.
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def extract_json_from_text(text: str) -> Optional[dict]:
    """
    Extract the first JSON object from a text that may contain prose.

    Handles cases where an LLM wraps JSON in markdown code fences or
    includes explanation text before/after the JSON.
    """
    if not text:
        return None

    # Try direct parse first
    result = safe_parse_json(text.strip())
    if isinstance(result, dict):
        return result

    # Strip markdown code fences
    fence_pattern = r"```(?:json)?\s*([\s\S]*?)```"
    matches = re.findall(fence_pattern, text, re.IGNORECASE)
    for match in matches:
        result = safe_parse_json(match.strip())
        if isinstance(result, dict):
            return result

    # Find first { ... } block
    brace_pattern = r"\{[\s\S]*\}"
    match = re.search(brace_pattern, text)
    if match:
        result = safe_parse_json(match.group())
        if isinstance(result, dict):
            return result

    return None


def to_json_string(obj: Any) -> str:
    """Serialize an object to JSON string, handling common types."""
    return json.dumps(obj, default=str, ensure_ascii=False)
