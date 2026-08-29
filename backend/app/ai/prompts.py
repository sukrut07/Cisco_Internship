"""
NetSage AI — Diagnosis Prompt Builder.

Loads and formats prompts from the prompts/ directory.
Keeps prompts efficient — only includes relevant evidence.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.ai.base import DiagnosisContext

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"

SYSTEM_PROMPT = """You are NetSage AI, an AI-assisted Cisco network troubleshooting assistant.

Your role is to ASSIST human network engineers, NOT to autonomously configure networks.

RULES:
1. Analyze ONLY the supplied evidence: symptom, topology, and Cisco show-command outputs.
2. Do NOT invent evidence that is not in the provided outputs.
3. Separate CONFIRMED findings (supported by evidence) from HYPOTHESES (possible but unconfirmed).
4. If evidence is insufficient, say so clearly in 'limitations'.
5. Recommend the next diagnostic command to gather missing evidence.
6. Provide practical fix steps that a human engineer MUST review and approve before applying.
7. Your confidence labels (LOW/MEDIUM/HIGH) reflect diagnostic certainty, not probability of correctness.
8. The final recommendation MUST be reviewed by a human before any action is taken.

OUTPUT FORMAT:
Return ONLY valid JSON matching this exact schema:
{
  "root_cause": "string — the most likely root cause based on evidence",
  "confidence": "LOW|MEDIUM|HIGH",
  "confidence_score": 0.0,
  "evidence": [
    {"source": "show command name", "observation": "what was observed"}
  ],
  "osi_layer": "Layer 1|Layer 2|Layer 3|Layer 4|Layer 7",
  "concept": "string — networking concept involved",
  "next_command": "string — next diagnostic command to run",
  "fix_steps": ["step 1", "step 2", ...],
  "limitations": ["limitation 1", ...]
}

Do NOT include any text outside the JSON object."""

PROMPT_VERSION = "netsage-diagnose-v1"


def build_system_prompt() -> str:
    """Return the system prompt."""
    return SYSTEM_PROMPT


def build_diagnosis_prompt(context: "DiagnosisContext") -> str:
    """
    Build an efficient user prompt from the diagnosis context.

    Clearly marks Cisco show output as UNTRUSTED NETWORK EVIDENCE to prevent
    adversarial injection from user commands overriding system instructions.
    """
    parts = []

    parts.append(f"CASE ID: {context.case_id}")
    parts.append(f"\nSYMPTOM:\n{context.symptom}")
    parts.append(f"\nNETWORK TOPOLOGY:\n{context.topology}")

    if context.show_outputs:
        parts.append("\n=== UNTRUSTED NETWORK EVIDENCE (SHOW COMMAND OUTPUTS) ===")
        for cmd, output in context.show_outputs.items():
            # Truncate very long outputs to avoid token waste
            truncated = output[:3000] if len(output) > 3000 else output
            parts.append(f"\n--- {cmd} ---\n{truncated}")
        parts.append("\n=== END UNTRUSTED NETWORK EVIDENCE ===")

    if context.devices:
        parts.append("\nSTRUCTURED DEVICE CONFIGURATION:")
        parts.append(json.dumps(context.devices, indent=2))

    if context.rule_findings:
        parts.append("\nDETERMINISTIC RULE FINDINGS (for context only — do not blindly repeat):")
        for finding in context.rule_findings:
            parts.append(
                f"  [{finding.get('status')}] {finding.get('rule_name')}: {finding.get('message')}"
            )

    if context.expected_osi_layer:
        parts.append(f"\nHINT — Expected OSI Layer: {context.expected_osi_layer}")

    parts.append(
        "\nReturn your analysis as valid JSON only. No prose outside the JSON object."
    )

    return "\n".join(parts)


build_user_prompt = build_diagnosis_prompt


def get_prompt_version() -> str:
    """Return the current prompt version identifier."""
    return PROMPT_VERSION
