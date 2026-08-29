"""
NetSage AI — Base AI Provider Interface.

All AI providers must inherit from BaseAIProvider and implement diagnose().
The AI is an ASSISTANT — it never autonomously modifies network devices.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class DiagnosisContext:
    """Normalized context sent to AI for diagnosis."""

    case_id: str
    symptom: str
    topology: str
    show_outputs: dict[str, str] = field(default_factory=dict)
    devices: list[dict] = field(default_factory=list)
    rule_findings: list[dict] = field(default_factory=list)
    expected_osi_layer: Optional[str] = None
    expected_fault: Optional[str] = None  # hidden from AI in eval mode
    category: Optional[str] = None


@dataclass
class AIProviderResponse:
    """Raw response from an AI provider before validation."""

    raw_text: str
    provider_name: str
    model_name: str
    prompt_version: str
    success: bool
    error_message: Optional[str] = None
    parsed_json: Optional[dict] = None


class BaseAIProvider(ABC):
    """Abstract base for all AI diagnosis providers."""

    provider_name: str = "base"
    default_model: str = ""

    @abstractmethod
    def diagnose(self, context: DiagnosisContext) -> AIProviderResponse:
        """
        Send the diagnosis context to the AI and return the raw response.

        IMPORTANT:
        - The AI is an assistant only.
        - Never execute network commands autonomously.
        - Never return a fabricated response on failure.
        """
        ...

    @property
    def model(self) -> str:
        """Return the model name to use."""
        return self.default_model

    def build_prompt(self, context: DiagnosisContext) -> str:
        """Build the user prompt from the context."""
        from app.ai.prompts import build_diagnosis_prompt
        return build_diagnosis_prompt(context)
