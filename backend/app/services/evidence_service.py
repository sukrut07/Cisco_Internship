"""
NetSage AI — Evidence Service.

Provides queryable, structured access to Cisco show-command evidence stored in cases.
"""
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.core.security import normalize_command_name
from app.parsers.show_parser import cisco_parser
from app.schemas.evidence import CaseEvidenceItem, CaseEvidenceResponse
from app.services.case_service import case_service

logger = logging.getLogger(__name__)


class EvidenceService:
    """Service for retrieving and inspecting case evidence."""

    def get_case_evidence(self, db: Session, case_id: str) -> CaseEvidenceResponse:
        """
        Extract and parse all show command outputs associated with a case.

        Returns both raw and structured parsed evidence.
        """
        case = case_service.get_case(db, case_id)
        show_outputs = case.show_outputs_dict

        items: list[CaseEvidenceItem] = []
        for cmd_raw, output_text in show_outputs.items():
            cmd_norm = normalize_command_name(cmd_raw)
            parse_result = cisco_parser.parse(cmd_raw, output_text)

            items.append(
                CaseEvidenceItem(
                    command=cmd_raw,
                    output=output_text,
                    status=parse_result.get("status", "ok"),
                    parsed=parse_result.get("parsed"),
                )
            )

        return CaseEvidenceResponse(
            case_id=case.case_id,
            total_commands=len(items),
            evidence=items,
        )


evidence_service = EvidenceService()
