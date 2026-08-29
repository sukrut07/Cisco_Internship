"""
NetSage AI — AI Response Parser and Validator.

Validates AI JSON against Pydantic schema.
Implements evidence grounding check.
Never blindly trusts raw AI output.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, ValidationError

from app.utils.json_utils import extract_json_from_text

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schema for AI output
# ---------------------------------------------------------------------------

class AIEvidenceItem(BaseModel):
    source: str = Field(..., description="Show command name used as evidence source")
    observation: str = Field(..., description="What was observed in that output")


class AIOutput(BaseModel):
    """Validated AI diagnosis output schema."""

    root_cause: str = Field(..., min_length=5)
    confidence: str = Field(..., pattern="^(LOW|MEDIUM|HIGH)$")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    evidence: list[AIEvidenceItem] = Field(default_factory=list)
    osi_layer: str = Field(default="Unknown")
    concept: str = Field(default="General Networking")
    next_command: str = Field(default="")
    fix_steps: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: str) -> str:
        return v.upper()

    @field_validator("osi_layer")
    @classmethod
    def normalize_osi_layer(cls, v: str) -> str:
        # Normalize "3" → "Layer 3", "layer3" → "Layer 3", etc.
        import re
        m = re.search(r"(\d)", v)
        if m:
            return f"Layer {m.group(1)}"
        return v


# ---------------------------------------------------------------------------
# Evidence grounding
# ---------------------------------------------------------------------------

GROUNDING_STATUSES = {
    "GROUNDED": "All AI evidence citations found in supplied show outputs.",
    "PARTIALLY_GROUNDED": "Some AI evidence citations not found in supplied show outputs.",
    "UNGROUNDED": "AI evidence citations not found in supplied show outputs.",
}


def check_evidence_grounding(
    ai_evidence: list[AIEvidenceItem],
    supplied_show_outputs: dict[str, str],
) -> tuple[str, list[dict]]:
    """
    Check each AI evidence item against supplied show outputs.

    Returns:
        (grounding_status, grounding_details)
    """
    if not ai_evidence:
        return "GROUNDED", []

    from app.core.security import normalize_command_name

    normalized_outputs = {
        normalize_command_name(k): v for k, v in supplied_show_outputs.items()
    }

    grounding_details = []
    grounded_count = 0

    for item in ai_evidence:
        normalized_source = normalize_command_name(item.source)

        # Check if source command is in supplied outputs
        source_found = normalized_source in normalized_outputs

        # Check if observation text has any overlap with actual output
        observation_grounded = False
        if source_found:
            output_text = normalized_outputs[normalized_source].lower()
            # Extract key nouns from observation
            obs_words = [w.lower() for w in item.observation.split() if len(w) > 3]
            matched_words = [w for w in obs_words if w in output_text]
            observation_grounded = len(matched_words) >= max(1, len(obs_words) // 3)

        grounding_details.append(
            {
                "source": item.source,
                "observation": item.observation,
                "source_found": source_found,
                "observation_grounded": observation_grounded,
                "grounded": source_found and observation_grounded,
            }
        )

        if source_found and observation_grounded:
            grounded_count += 1

    total = len(ai_evidence)
    if grounded_count == total:
        status = "GROUNDED"
    elif grounded_count >= total * 0.5:
        status = "PARTIALLY_GROUNDED"
    else:
        status = "UNGROUNDED"

    return status, grounding_details


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------

class AIResponseParser:
    """Parses and validates raw AI text responses."""

    def parse(
        self,
        raw_text: str,
        supplied_show_outputs: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Parse and validate an AI response.

        Returns:
            {
              "success": bool,
              "ai_output": AIOutput | None,
              "grounding_status": str,
              "grounding_details": list,
              "error": str | None,
              "raw_text": str
            }
        """
        if not raw_text:
            return self._error("AI returned empty response.", raw_text)

        # Step 1: Extract JSON
        parsed_json = extract_json_from_text(raw_text)
        if parsed_json is None:
            return self._error("Could not extract JSON from AI response.", raw_text)

        # Step 2: Validate with Pydantic
        try:
            ai_output = AIOutput.model_validate(parsed_json)
        except ValidationError as exc:
            logger.warning("AI output failed Pydantic validation: %s", exc)
            return self._error(f"AI output schema validation failed: {exc}", raw_text)

        # Step 3: Evidence grounding
        grounding_status = "GROUNDED"
        grounding_details: list[dict] = []

        if supplied_show_outputs:
            grounding_status, grounding_details = check_evidence_grounding(
                ai_output.evidence, supplied_show_outputs
            )

            if grounding_status != "GROUNDED":
                logger.warning(
                    "AI evidence grounding: %s (%d items)",
                    grounding_status,
                    len(grounding_details),
                )

        return {
            "success": True,
            "ai_output": ai_output,
            "grounding_status": grounding_status,
            "grounding_details": grounding_details,
            "error": None,
            "raw_text": raw_text,
        }

    @staticmethod
    def _error(message: str, raw_text: str) -> dict[str, Any]:
        return {
            "success": False,
            "ai_output": None,
            "grounding_status": "UNGROUNDED",
            "grounding_details": [],
            "error": message,
            "raw_text": raw_text,
        }


# Module-level singleton
ai_response_parser = AIResponseParser()
