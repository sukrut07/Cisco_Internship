"""
NetSage AI — Gemini Provider.
"""
from __future__ import annotations

import json
import logging

from app.ai.base import BaseAIProvider, DiagnosisContext, AIProviderResponse
from app.ai.prompts import build_system_prompt, get_prompt_version
from app.core.config import get_settings
from app.core.exceptions import AIProviderError

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Google Gemini AI provider."""

    provider_name = "gemini"
    default_model = "gemini-1.5-flash"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.ai_api_key
        self._model = settings.ai_model or self.default_model

    def diagnose(self, context: DiagnosisContext) -> AIProviderResponse:
        """Call Gemini API for diagnosis."""
        try:
            import google.generativeai as genai
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

        try:
            response = model.generate_content(
                user_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=2000,
                    response_mime_type="application/json",
                ),
            )
            raw_text = response.text or ""
            return AIProviderResponse(
                raw_text=raw_text,
                provider_name=self.provider_name,
                model_name=self._model,
                prompt_version=get_prompt_version(),
                success=True,
            )
        except Exception as exc:
            logger.error("Gemini API error: %s", exc)
            raise AIProviderError(f"Gemini API error: {exc}")


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude provider."""

    provider_name = "anthropic"
    default_model = "claude-3-5-sonnet-20241022"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.ai_api_key
        self._model = settings.ai_model or self.default_model

    def diagnose(self, context: DiagnosisContext) -> AIProviderResponse:
        """Call Anthropic Claude API."""
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

        try:
            message = client.messages.create(
                model=self._model,
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw_text = message.content[0].text if message.content else ""
            return AIProviderResponse(
                raw_text=raw_text,
                provider_name=self.provider_name,
                model_name=self._model,
                prompt_version=get_prompt_version(),
                success=True,
            )
        except Exception as exc:
            logger.error("Anthropic API error: %s", exc)
            raise AIProviderError(f"Anthropic API error: {exc}")
