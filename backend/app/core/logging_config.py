"""
NetSage AI — Structured Logging Configuration.
"""
from __future__ import annotations

import logging
import sys
from typing import Any


def configure_logging(level: str = "INFO") -> None:
    """Configure application-wide logging."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=date_fmt))
    handler.setLevel(log_level)

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()
    root.addHandler(handler)

    # Silence noisy libraries in production
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if level.upper() == "DEBUG" else logging.WARNING
    )
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)


class RequestContextFilter(logging.Filter):
    """Inject request_id into log records when available."""

    def filter(self, record: Any) -> bool:  # noqa: ANN001
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True
