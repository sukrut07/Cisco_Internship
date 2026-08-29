"""
NetSage AI — ACL Rule.

Detects ACL deny entries with matches that may be blocking traffic.
"""
from __future__ import annotations

from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.parsers.acl_parser import parse_access_lists, has_deny_rules


class ACLRule(BaseRule):
    """Check for ACL deny entries that may be blocking traffic."""

    name = "acl_blocking"
    description = "Detects ACL deny rules with match counts."

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

        deny_entries = []
        for acl in acls:
            for entry in acl.get("entries", []):
                if entry.get("action") == "deny" and entry.get("matches", 0) > 0:
                    deny_entries.append(
                        f"ACL {acl['acl_name']} seq {entry['sequence']}: "
                        f"deny {entry.get('protocol', 'ip')} "
                        f"{entry.get('source', 'any')} {entry.get('destination', 'any')} "
                        f"({entry['matches']} matches)"
                    )

        if not deny_entries:
            return self._pass(
                f"Reviewed {len(acls)} ACL(s). No deny entries with matches found."
            )

        return self._fail(
            message="ACL deny entries with matches detected — may be blocking traffic.",
            severity="HIGH",
            evidence=deny_entries,
            details={"deny_entry_count": len(deny_entries)},
        )
