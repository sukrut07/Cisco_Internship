"""
NetSage AI — Anthropic Claude Provider.

Separated from gemini_provider.py into its own module for clarity.
"""
from __future__ import annotations

import logging
from typing import Any

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from app.ai.base import BaseAIProvider, DiagnosisContext, AIProviderResponse
from app.ai.prompts import build_system_prompt, get_prompt_version
from app.core.config import get_settings
from app.core.exceptions import (
    AIProviderError,
    AIProviderTimeout,
    AIAuthenticationError,
    AIQuotaError,
)

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude provider."""

    provider_name = "anthropic"
    default_model = "claude-3-5-sonnet-20241022"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.ai_api_key
        self._model = settings.ai_model or self.default_model
        self._timeout = settings.ai_timeout_seconds
        self._max_retries = settings.ai_max_retries

    def diagnose(self, context: DiagnosisContext) -> AIProviderResponse:
        """Call Anthropic Claude API with retry and timeout."""
        try:
            import anthropic
        except ImportError:
            raise AIProviderError(
                "anthropic package not installed. Run: pip install anthropic"
            )

        if not self._api_key:
            raise AIProviderError("AI_API_KEY not configured for Anthropic provider.")

        client = anthropic.Anthropic(api_key=self._api_key)
        user_prompt = self.build_prompt(context)
        system_prompt = build_system_prompt()

        logger.info("Calling Anthropic API (model=%s, case=%s)", self._model, context.case_id)

        retryable_types = (
            anthropic.RateLimitError,
            anthropic.APITimeoutError,
            anthropic.APIConnectionError,
            anthropic.InternalServerError,
        )

        @retry(
            retry=retry_if_exception_type(retryable_types),
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )
        def _call() -> Any:
            return client.messages.create(
                model=self._model,
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                timeout=self._timeout,
            )

        try:
            message = _call()
            raw_text = message.content[0].text if message.content else ""
            return AIProviderResponse(
                raw_text=raw_text,
                provider_name=self.provider_name,
                model_name=self._model,
                prompt_version=get_prompt_version(),
                success=True,
            )
        except anthropic.AuthenticationError as exc:
            logger.error("Anthropic authentication error")
            raise AIAuthenticationError(f"Anthropic authentication failed: {exc}")
        except anthropic.RateLimitError as exc:
            logger.error("Anthropic rate limit hit")
            raise AIQuotaError(f"Anthropic rate limit exceeded: {exc}")
        except anthropic.APITimeoutError as exc:
            logger.error("Anthropic request timed out after %ds", self._timeout)
            raise AIProviderTimeout(f"Anthropic request timed out after {self._timeout}s: {exc}")
        except Exception as exc:
            logger.error("Anthropic API error: %s", exc)
            raise AIProviderError(f"Anthropic API error: {exc}")
