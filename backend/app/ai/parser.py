"""
NetSage AI — AI Response Parser and Validator.

Validates AI JSON against Pydantic schema.
Implements multi-dimensional evidence grounding check.
Never blindly trusts raw AI output.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, ValidationError

from app.core.security import normalize_command_name
from app.utils.ip_utils import extract_ips_from_text
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
    alternative_causes: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    safety_notes: Optional[str] = Field(default="")

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: str) -> str:
        return v.upper()

    @field_validator("osi_layer")
    @classmethod
    def normalize_osi_layer(cls, v: str) -> str:
        # Normalize "3" → "Layer 3", "layer3" → "Layer 3", etc.
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

# Common network interface patterns (e.g., Gi0/1, FastEthernet0/0, VLAN 10)
_IFACE_PATTERN = re.compile(
    r"\b(?:gigabitethernet|fastethernet|ethernet|tengigabitethernet|serial|vlan|loopback|gi|fa|eth|se|vl|lo)\s*[\d\/\.]+\b",
    re.IGNORECASE,
)
_VLAN_PATTERN = re.compile(r"\bvlan\s+(\d+)\b", re.IGNORECASE)
_IP_NET_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b")


def _is_observation_grounded(observation: str, output_text: str) -> bool:
    """
    Perform a multi-signal check to determine if an AI observation is grounded in show output text.

    Checks:
    1. Direct substring match (case-insensitive).
    2. IP addresses / Subnets mentioned in observation must exist in output.
    3. Interface names mentioned in observation must exist in output.
    4. VLAN IDs mentioned in observation must exist in output.
    5. Key domain technical terms (down, admin, denied, nat, route, etc.) overlap.
    6. Informative keyword token overlap.
    """
    obs_lower = observation.lower().strip()
    out_lower = output_text.lower()

    # 1. Direct match
    if obs_lower in out_lower:
        return True

    # 2. IP / Subnet check
    obs_ips = _IP_NET_PATTERN.findall(observation)
    if obs_ips:
        for ip in obs_ips:
            if ip.lower() in out_lower:
                return True

    # 3. Interface check
    obs_ifaces = _IFACE_PATTERN.findall(observation)
    if obs_ifaces:
        for iface in obs_ifaces:
            norm_iface = re.sub(r"\s+", "", iface.lower())
            if norm_iface in out_lower.replace(" ", ""):
                return True

    # 4. VLAN check
    obs_vlans = _VLAN_PATTERN.findall(observation)
    if obs_vlans:
        for vlan in obs_vlans:
            if vlan in out_lower:
                return True

    # 5. Technical status terms check
    tech_phrases = [
        "administratively down",
        "admin down",
        "down/down",
        "up/up",
        "up/down",
        "denied",
        "matches",
        "no translation",
        "translation",
        "apipa",
        "169.254",
        "pool exhausted",
        "missing route",
        "no route",
        "directly connected",
        "gateway of last resort",
    ]
    for phrase in tech_phrases:
        if phrase in obs_lower and phrase in out_lower:
            return True

    # 6. Informative token overlap (stopwords filtered)
    stopwords = {
        "the", "and", "that", "this", "with", "from", "for", "are", "was", "were",
        "been", "have", "has", "had", "does", "did", "show", "output", "configured",
        "interface", "device", "router", "switch", "port", "network", "command"
    }
    obs_tokens = [
        w.strip(".,;:\"'()[]{}")
        for w in obs_lower.split()
        if len(w) > 3 and w not in stopwords
    ]
    if not obs_tokens:
        return True  # Observation had no specific claims

    matched_tokens = [w for w in obs_tokens if w in out_lower]
    return len(matched_tokens) >= max(1, len(obs_tokens) // 3)


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

    normalized_outputs = {
        normalize_command_name(k): v for k, v in supplied_show_outputs.items()
    }

    grounding_details = []
    grounded_count = 0

    for item in ai_evidence:
        normalized_source = normalize_command_name(item.source)

        # Check exact or prefix matching for source command
        matched_cmd_key = None
        if normalized_source in normalized_outputs:
            matched_cmd_key = normalized_source
        else:
            for k in normalized_outputs:
                if normalized_source.startswith(k) or k.startswith(normalized_source):
                    matched_cmd_key = k
                    break

        source_found = matched_cmd_key is not None
        observation_grounded = False

        if source_found and matched_cmd_key:
            output_text = normalized_outputs[matched_cmd_key]
            observation_grounded = _is_observation_grounded(item.observation, output_text)

        is_item_grounded = source_found and observation_grounded
        if is_item_grounded:
            grounded_count += 1

        grounding_details.append(
            {
                "source": item.source,
                "observation": item.observation,
                "source_found": source_found,
                "observation_grounded": observation_grounded,
                "grounded": is_item_grounded,
            }
        )

    total = len(ai_evidence)
    if grounded_count == total:
        status = "GROUNDED"
    elif grounded_count > 0:
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
