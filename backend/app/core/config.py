"""
NetSage AI — Application Configuration.

Reads all settings from environment variables / .env file.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./netsage.db"

    # AI Provider
    ai_provider: str = "mock"          # mock | openai | gemini | anthropic
    ai_model: str = ""
    ai_api_key: str = ""
    ai_fallback_provider: Optional[str] = None

    # Logging
    log_level: str = "INFO"

    # CORS — stored as comma-separated string, parsed into list
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8501"

    # Security
    secret_key: str = "change-me-in-production"

    # Prompts
    prompt_version: str = "netsage-diagnose-v1"

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
