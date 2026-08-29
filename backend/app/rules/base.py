"""
NetSage AI — Base Rule Interface.

All rules must inherit from BaseRule and implement check().
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class RuleCheckResult:
    """Standard output for every rule check."""

    rule_name: str
    status: str  # PASS | FAIL | WARNING | NOT_CHECKED
    severity: str  # LOW | MEDIUM | HIGH | CRITICAL
    message: str
    evidence: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_name": self.rule_name,
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
            "evidence": self.evidence,
            "details": self.details,
        }


class BaseRule(ABC):
    """Abstract base class for all deterministic network rules."""

    name: str = "base_rule"
    description: str = ""

    @abstractmethod
    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        """
        Run the rule check against the provided context.

        context keys (all optional — rule must handle missing data gracefully):
          - symptom: str
          - topology: str
          - show_outputs: dict[str, str]  raw show command text
          - parsed_outputs: dict  already-parsed structured data
          - devices: list[dict]  structured device config
          - interfaces: list[dict]
          - routes: list[dict]
          - vlans: list[dict]
          - trunks: list[dict]
          - acls: list[dict]
          - nat_translations: list[dict]
          - dhcp_bindings: list[dict]
          - expected_vlan: str | None
          - destination_network: str | None
        """
        ...

    def _not_checked(self, reason: str = "Insufficient evidence") -> RuleCheckResult:
        return RuleCheckResult(
            rule_name=self.name,
            status="NOT_CHECKED",
            severity="LOW",
            message=reason,
        )

    def _pass(self, message: str, evidence: Optional[list] = None) -> RuleCheckResult:
        return RuleCheckResult(
            rule_name=self.name,
            status="PASS",
            severity="LOW",
            message=message,
            evidence=evidence or [],
        )

    def _fail(
        self,
        message: str,
        severity: str = "HIGH",
        evidence: Optional[list] = None,
        details: Optional[dict] = None,
    ) -> RuleCheckResult:
        return RuleCheckResult(
            rule_name=self.name,
            status="FAIL",
            severity=severity,
            message=message,
            evidence=evidence or [],
            details=details or {},
        )

    def _warning(
        self,
        message: str,
        severity: str = "MEDIUM",
        evidence: Optional[list] = None,
        details: Optional[dict] = None,
    ) -> RuleCheckResult:
        return RuleCheckResult(
            rule_name=self.name,
            status="WARNING",
            severity=severity,
            message=message,
            evidence=evidence or [],
            details=details or {},
        )
