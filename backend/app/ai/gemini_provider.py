"""
NetSage AI — Gemini Provider.
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
from app.core.exceptions import AIProviderError, AIProviderTimeout, AIQuotaError

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Google Gemini AI provider."""

    provider_name = "gemini"
    default_model = "gemini-1.5-flash"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.ai_api_key
        self._model = settings.ai_model or self.default_model
        self._timeout = settings.ai_timeout_seconds
        self._max_retries = settings.ai_max_retries

    def diagnose(self, context: DiagnosisContext) -> AIProviderResponse:
        """Call Gemini API for diagnosis with retry and timeout."""
        try:
            import google.generativeai as genai
            from google.api_core import exceptions as google_exceptions
        except ImportError:
            raise AIProviderError(
                "google-generativeai package not installed. Run: pip install google-generativeai"
            )

        if not self._api_key:
            raise AIProviderError("AI_API_KEY not configured for Gemini provider.")

        genai.configure(api_key=self._api_key)
        model = genai.GenerativeModel(
            model_name=self._model,
            system_instruction=build_system_prompt(),
        )

        user_prompt = self.build_prompt(context)
        logger.info("Calling Gemini API (model=%s, case=%s)", self._model, context.case_id)

        retryable_exceptions = (
            google_exceptions.ResourceExhausted,
            google_exceptions.ServiceUnavailable,
            google_exceptions.DeadlineExceeded,
            google_exceptions.InternalServerError,
        )

        @retry(
            retry=retry_if_exception_type(retryable_exceptions),
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )
        def _call() -> Any:
            return model.generate_content(
                user_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=2000,
                    response_mime_type="application/json",
                ),
                request_options={"timeout": self._timeout},
            )

        try:
            response = _call()
            raw_text = response.text or ""
            return AIProviderResponse(
                raw_text=raw_text,
                provider_name=self.provider_name,
                model_name=self._model,
                prompt_version=get_prompt_version(),
                success=True,
            )
        except google_exceptions.Unauthenticated as exc:
            logger.error("Gemini authentication failed")
            raise AIProviderError(f"Gemini authentication failed: {exc}")
        except google_exceptions.PermissionDenied as exc:
            logger.error("Gemini permission denied")
            raise AIProviderError(f"Gemini permission denied: {exc}")
        except google_exceptions.DeadlineExceeded as exc:
            logger.error("Gemini request timed out after %ds", self._timeout)
            raise AIProviderTimeout(f"Gemini request timed out after {self._timeout}s: {exc}")
        except google_exceptions.ResourceExhausted as exc:
            logger.error("Gemini quota / rate limit exceeded")
            raise AIQuotaError(f"Gemini quota / rate limit exceeded: {exc}")
        except Exception as exc:
            logger.error("Gemini API error: %s", exc)
            raise AIProviderError(f"Gemini API error: {exc}")


