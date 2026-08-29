"""
NetSage AI — ACL Rule.

Detects ACL deny entries with matches or explicit deny rules that may be blocking traffic.
"""
from __future__ import annotations

from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.parsers.acl_parser import parse_access_lists, has_deny_rules


class ACLRule(BaseRule):
    """Check for ACL deny entries and traffic filters that may be blocking traffic."""

    name = "acl_blocking"
    description = "Detects ACL deny rules with match counts or blocking filters."

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        show_outputs: dict = context.get("show_outputs", {})
        acls: list[dict] = context.get("acls", [])

        if not acls:
            raw = show_outputs.get("show access-lists") or show_outputs.get(
                "show ip access-lists", ""
            )
            if raw:
                acls = parse_access_lists(raw)

        if not acls:
            return self._not_checked("No ACL output available.")

        matched_deny_entries = []
        all_deny_entries = []

        for acl in acls:
            for entry in acl.get("entries", []):
                if entry.get("action") == "deny":
                    entry_desc = (
                        f"ACL {acl['acl_name']} seq {entry.get('sequence', 'N/A')}: "
                        f"deny {entry.get('protocol', 'ip')} "
                        f"{entry.get('source', 'any')} {entry.get('destination', 'any')}"
                    )
                    matches = entry.get("matches", 0)
                    if matches > 0:
                        matched_deny_entries.append(f"{entry_desc} ({matches} matches)")
                    else:
                        all_deny_entries.append(entry_desc)

        if matched_deny_entries:
            return self._fail(
                message="ACL deny entries with active match counts detected — blocking traffic.",
                severity="HIGH",
                evidence=matched_deny_entries,
                details={"matched_deny_count": len(matched_deny_entries)},
            )

        if all_deny_entries:
            return self._warning(
                message="ACL contains explicit deny rules. Verify if traffic matches these rules.",
                severity="MEDIUM",
                evidence=all_deny_entries,
                details={"deny_rule_count": len(all_deny_entries)},
            )

        return self._pass(
            f"Reviewed {len(acls)} ACL(s). No active deny entries found."
        )
