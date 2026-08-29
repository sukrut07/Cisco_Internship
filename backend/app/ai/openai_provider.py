"""
NetSage AI — OpenAI Provider.
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
from app.core.exceptions import AIProviderError

logger = logging.getLogger(__name__)


def _is_retryable_openai_error(exc: Exception) -> bool:
    """Return True for transient OpenAI errors that should be retried."""
    try:
        import openai
        return isinstance(exc, (
            openai.APIConnectionError,
            openai.RateLimitError,
            openai.APITimeoutError,
            openai.InternalServerError,
        ))
    except ImportError:
        return False


class OpenAIProvider(BaseAIProvider):
    """Real OpenAI GPT provider for production use."""

    provider_name = "openai"
    default_model = "gpt-4o"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.ai_api_key
        self._model = settings.ai_model or self.default_model
        self._timeout = settings.ai_timeout_seconds
        self._max_retries = settings.ai_max_retries

    def diagnose(self, context: DiagnosisContext) -> AIProviderResponse:
        """Call OpenAI API for diagnosis with retry and timeout."""
        try:
            import openai
        except ImportError:
            raise AIProviderError("openai package not installed. Run: pip install openai")

        if not self._api_key:
            raise AIProviderError("AI_API_KEY not configured for OpenAI provider.")

        client = openai.OpenAI(api_key=self._api_key, timeout=self._timeout)
        user_prompt = self.build_prompt(context)
        system_prompt = build_system_prompt()

        logger.info("Calling OpenAI API (model=%s, case=%s)", self._model, context.case_id)

        @retry(
            retry=retry_if_exception_type(tuple(self._retryable_types())),
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )
        def _call() -> Any:
            return client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )

        try:
            response = _call()
            raw_text = response.choices[0].message.content or ""
            return AIProviderResponse(
                raw_text=raw_text,
                provider_name=self.provider_name,
                model_name=self._model,
                prompt_version=get_prompt_version(),
                success=True,
            )
        except openai.AuthenticationError as exc:
            logger.error("OpenAI authentication error")
            raise AIProviderError(f"OpenAI authentication failed — check AI_API_KEY: {exc}")
        except openai.APITimeoutError as exc:
            logger.error("OpenAI request timed out after %ds", self._timeout)
            raise AIProviderError(f"OpenAI request timed out after {self._timeout}s: {exc}")
        except openai.RateLimitError as exc:
            logger.error("OpenAI rate limit exceeded after %d retries", self._max_retries)
            raise AIProviderError(f"OpenAI rate limit exceeded: {exc}")
        except openai.APIError as exc:
            logger.error("OpenAI API error: %s", exc)
            raise AIProviderError(f"OpenAI API error: {exc}")
        except Exception as exc:
            logger.error("Unexpected error calling OpenAI: %s", exc)
            raise AIProviderError(f"Unexpected error: {exc}")

    @staticmethod
    def _retryable_types() -> list:
        """Return list of OpenAI exception types that are safe to retry."""
        try:
            import openai
            return [
                openai.APIConnectionError,
                openai.RateLimitError,
                openai.APITimeoutError,
                openai.InternalServerError,
            ]
        except ImportError:
            return []
