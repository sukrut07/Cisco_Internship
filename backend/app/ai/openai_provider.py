"""
NetSage AI — OpenAI Provider.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from app.ai.base import BaseAIProvider, DiagnosisContext, AIProviderResponse
from app.ai.prompts import build_system_prompt, get_prompt_version
from app.core.config import get_settings
from app.core.exceptions import AIProviderError

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """Real OpenAI GPT provider for production use."""

    provider_name = "openai"
    default_model = "gpt-4o"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.ai_api_key
        self._model = settings.ai_model or self.default_model

    def diagnose(self, context: DiagnosisContext) -> AIProviderResponse:
        """Call OpenAI API for diagnosis."""
        try:
            import openai
        except ImportError:
            raise AIProviderError("openai package not installed. Run: pip install openai")

        if not self._api_key:
            raise AIProviderError("AI_API_KEY not configured for OpenAI provider.")

        client = openai.OpenAI(api_key=self._api_key)
        user_prompt = self.build_prompt(context)
        system_prompt = build_system_prompt()

        logger.info("Calling OpenAI API (model=%s, case=%s)", self._model, context.case_id)

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,  # Low temperature for deterministic technical output
                max_tokens=2000,
                response_format={"type": "json_object"},
            )
            raw_text = response.choices[0].message.content or ""
            return AIProviderResponse(
                raw_text=raw_text,
                provider_name=self.provider_name,
                model_name=self._model,
                prompt_version=get_prompt_version(),
                success=True,
            )
        except openai.APIError as exc:
            logger.error("OpenAI API error: %s", exc)
            raise AIProviderError(f"OpenAI API error: {exc}")
        except Exception as exc:
            logger.error("Unexpected error calling OpenAI: %s", exc)
            raise AIProviderError(f"Unexpected error: {exc}")
