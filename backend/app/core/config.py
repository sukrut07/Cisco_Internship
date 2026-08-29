"""
NetSage AI — Application Configuration.

Reads all settings from environment variables / .env file.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "NetSage AI"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False  # Explicitly false; set DEBUG=true in .env for local dev

    # Database
    database_url: str = "sqlite:///./netsage.db"

    # AI Provider
    ai_provider: str = "mock"           # mock | openai | gemini | anthropic
    ai_model: str = ""
    ai_api_key: str = ""
    ai_fallback_provider: Optional[str] = None
    ai_timeout_seconds: int = 30        # HTTP timeout for all AI provider calls
    ai_max_retries: int = 3             # Max retry attempts on transient errors

    # Logging
    log_level: str = "INFO"

    # CORS — stored as comma-separated string, parsed into list
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8501"

    # Security
    secret_key: str = "change-me-in-production"
    require_auth: bool = False           # Set REQUIRE_AUTH=true to enable API-key auth
    api_key: str = ""                    # API key value when REQUIRE_AUTH=true

    # Request size limits
    max_request_body_mb: int = 5         # Max HTTP body size in megabytes
    max_show_output_chars: int = 30_000  # Max characters in total show outputs
    max_command_output_chars: int = 5_000  # Max chars per individual command output

    # Rate limiting
    rate_limit_enabled: bool = False     # Set RATE_LIMIT_ENABLED=true in production
    rate_limit_diagnose: str = "10/minute"
    rate_limit_default: str = "100/minute"

    # Prompts
    prompt_version: str = "netsage-diagnose-v1"

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    def warn_production_defaults(self) -> None:
        """Log warnings if production-unsafe defaults are in use."""
        if self.is_production:
            if self.secret_key == "change-me-in-production":
                logger.critical(
                    "SECRET_KEY is set to the insecure default! "
                    "Set a strong SECRET_KEY environment variable in production."
                )
            if self.ai_provider != "mock" and not self.ai_api_key:
                logger.warning(
                    "AI_API_KEY is not set but AI_PROVIDER=%s", self.ai_provider
                )
            if self.debug:
                logger.warning("DEBUG=true in production — disable this.")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
