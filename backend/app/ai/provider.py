"""
NetSage AI — AI Provider Factory.

Selects the correct AI provider based on the AI_PROVIDER environment variable.
Never tightly couples the application to a single provider.
"""
from __future__ import annotations

import logging

from app.ai.base import BaseAIProvider
from app.core.config import get_settings
from app.core.exceptions import AIProviderError

logger = logging.getLogger(__name__)

_PROVIDER_MAP = {
    "mock": "app.ai.mock_provider.MockAIProvider",
    "openai": "app.ai.openai_provider.OpenAIProvider",
    "gemini": "app.ai.gemini_provider.GeminiProvider",
    "anthropic": "app.ai.gemini_provider.AnthropicProvider",
}


def get_ai_provider() -> BaseAIProvider:
    """
    Return the configured AI provider instance.

    Falls back to mock if configured or if provider fails to initialize.
    Never fabricates a response on failure.
    """
    settings = get_settings()
    provider_name = settings.ai_provider.lower().strip()

    if provider_name not in _PROVIDER_MAP:
        logger.warning(
            "Unknown AI provider '%s'. Falling back to mock.", provider_name
        )
        provider_name = "mock"

    class_path = _PROVIDER_MAP[provider_name]
    module_path, class_name = class_path.rsplit(".", 1)

    try:
        import importlib
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        provider = cls()
        logger.info("AI provider initialized: %s", provider_name)
        return provider
    except Exception as exc:
        # Check if fallback is configured
        fallback = (settings.ai_fallback_provider or "").lower()
        if fallback == "mock" or (provider_name != "mock"):
            logger.warning(
                "Failed to initialize '%s' provider (%s). Falling back to mock.",
                provider_name,
                exc,
            )
            from app.ai.mock_provider import MockAIProvider
            return MockAIProvider()

        raise AIProviderError(
            f"Failed to initialize AI provider '{provider_name}': {exc}"
        )


def get_provider_name() -> str:
    """Return the name of the configured AI provider."""
    return get_settings().ai_provider.lower()
