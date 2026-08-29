"""
NetSage AI — Diagnosis Service.

Orchestrates the complete diagnosis pipeline:
  Load case → Merge evidence → Parse show outputs → Run rules →
  Build AI context → Call AI → Validate → Ground evidence →
  Calculate confidence → Compare → Store → Return review package.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.ai.base import DiagnosisContext
from app.ai.parser import ai_response_parser
from app.ai.provider import get_ai_provider
from app.core.exceptions import (
    AIProviderError,
    AIResponseParseError,
    CaseNotFoundError,
    DiagnosisNotFoundError,
)
from app.core.security import normalize_command_name
from app.models.case import Case
from app.models.diagnosis import Diagnosis
from app.models.rule_result import RuleResult
from app.parsers.show_parser import cisco_parser
from app.rules.engine import rule_engine
from app.schemas.diagnosis import DiagnoseRequest, DiagnosisResponse, ComparisonResult, DiagnoseResponse
from app.services.audit_service import audit_service
from app.services.case_service import case_service
from app.services.comparison_service import comparison_service
from app.utils.confidence import ConfidenceSignals, calculate_confidence

logger = logging.getLogger(__name__)


class DiagnosisService:
    """Orchestrates the complete diagnosis pipeline."""

    def run_diagnosis(
        self,
        db: Session,
        case_id: str,
        request: Optional[DiagnoseRequest] = None,
    ) -> DiagnoseResponse:
        """
        Execute the full diagnosis pipeline for a case.

        Step:
        1. Load case
        2. Merge runtime evidence
        3. Normalize show outputs
        4. Parse show outputs
        5. Build rule context
        6. Run rule engine
        7. Build AI context
        8. Call AI provider
        9. Parse and validate AI JSON
        10. Ground AI evidence
        11. Calculate composite confidence
        12. Compare AI + rules
        13. Store diagnosis
        14. Store rule results
        15. Transition workflow state
        16. Create audit event
        17. Return review package
        """
        request_id = str(uuid.uuid4())
        logger.info("Starting diagnosis for case %s (request_id=%s)", case_id, request_id)

        # Step 1: Load case
        case = case_service.get_case(db, case_id)

        # Step 2: Merge evidence (runtime request overrides stored case data)
        req = request or DiagnoseRequest()
        symptom = req.symptom or case.symptom
        topology = req.topology or case.topology
        show_outputs_raw: dict[str, str] = case.show_outputs_dict.copy()
        if req.show_outputs:
            show_outputs_raw.update(req.show_outputs)
        devices: list[dict] = req.devices or []
        destination_network = req.destination_network
        expected_vlan = req.expected_vlan

        # Step 3: Normalize show output keys
        show_outputs: dict[str, str] = {
            normalize_command_name(k): v for k, v in show_outputs_raw.items()
        }

        # Step 4: Parse show outputs
        parsed = cisco_parser.parse_all(show_outputs)
        interfaces = cisco_parser.get_interfaces(show_outputs)
        routes = cisco_parser.get_routes(show_outputs)
        vlans = cisco_parser.get_vlans(show_outputs)
        trunks = cisco_parser.get_trunks(show_outputs)
        acls = cisco_parser.get_acls(show_outputs)
        nat_translations = cisco_parser.get_nat_translations(show_outputs)
        dhcp_bindings = cisco_parser.get_dhcp_bindings(show_outputs)

        # Step 5: Build rule context
        rule_context = {
            "symptom": symptom,
            "topology": topology,
            "show_outputs": show_outputs,
            "devices": devices,
            "interfaces": interfaces,
            "routes": routes,
            "vlans": vlans,
            "trunks": trunks,
            "acls": acls,
            "nat_translations": nat_translations,
            "dhcp_bindings": dhcp_bindings,
            "destination_network": destination_network,
            "expected_vlan": expected_vlan,
        }

        # Step 6: Run rule engine
        audit_service.log(
            db, "DIAGNOSIS_REQUESTED", f"Diagnosis requested for {case_id}", case_id
        )
        rule_results = rule_engine.run_all(rule_context)
        rule_findings_for_ai = [
            {"rule_name": r.rule_name, "status": r.status, "message": r.message}
            for r in rule_results if r.status in ("FAIL", "WARNING")
        ]

        audit_service.log(
            db,
            "RULE_CHECK_COMPLETED",
            f"Rule check completed: {rule_engine.summary(rule_results)}",
            case_id,
            metadata={"summary": rule_engine.summary(rule_results)},
        )

        # Step 7: Build AI context
        ai_context = DiagnosisContext(
            case_id=case_id,
            symptom=symptom,
            topology=topology,
            show_outputs=show_outputs,
            devices=devices,
            rule_findings=rule_findings_for_ai,
            expected_osi_layer=case.expected_osi_layer,
            category=case.category,
        )

        # Step 8: Call AI provider
        provider = get_ai_provider()
        logger.info("Calling AI provider: %s", provider.provider_name)

        try:
            ai_response = provider.diagnose(ai_context)
        except AIProviderError as exc:
            logger.error("AI provider error: %s", exc)
            raise

        if not ai_response.success:
            raise AIProviderError(
                f"AI provider returned failure: {ai_response.error_message}"
            )

        # Step 9 & 10: Parse, validate, ground evidence
        parse_result = ai_response_parser.parse(
            ai_response.raw_text, show_outputs
        )

        if not parse_result["success"]:
            raise AIResponseParseError(
                f"AI response parse failed: {parse_result['error']}"
            )

        ai_output = parse_result["ai_output"]
        grounding_status = parse_result["grounding_status"]

        audit_service.log(
            db,
            "AI_DIAGNOSIS_COMPLETED",
            f"AI diagnosis complete. Provider: {provider.provider_name}, grounding: {grounding_status}",
            case_id,
            metadata={
                "provider": provider.provider_name,
                "model": ai_response.model_name,
                "grounding_status": grounding_status,
            },
        )

        # Step 11: Calculate composite confidence
        failed_rules = rule_engine.get_failures(rule_results)
        signals = ConfidenceSignals(
            ai_confidence=ai_output.confidence,
            ai_confidence_score=ai_output.confidence_score,
            rule_agreement=len(failed_rules) > 0,  # Rules found issues (implies they checked)
            rule_fail_count=len(failed_rules),
            grounding_status=grounding_status,
        )
        composite_score, composite_label = calculate_confidence(signals)

        # Step 12: Compare AI + rules
        comparison = comparison_service.compare(
            ai_root_cause=ai_output.root_cause,
            ai_osi_layer=ai_output.osi_layer,
            rule_results=rule_results,
            grounding_status=grounding_status,
            expected_fault=case.expected_fault,
        )

        audit_service.log(
            db,
            "COMPARISON_COMPLETED",
            f"Comparison: {comparison['agreement_type']}, grounding: {grounding_status}",
            case_id,
            metadata=comparison,
        )

        # Step 13: Store diagnosis
        diag = Diagnosis(
            case_id=case_id,
            root_cause=ai_output.root_cause,
            confidence=composite_label,
            confidence_score=composite_score,
            osi_layer=ai_output.osi_layer,
            concept=ai_output.concept,
            next_command=ai_output.next_command,
            ai_provider=provider.provider_name,
            model_name=ai_response.model_name,
            prompt_version=ai_response.prompt_version,
            raw_response=ai_response.raw_text[:50000] if ai_response.raw_text else None,
            grounding_status=grounding_status,
        )
        diag.evidence_list = [e.model_dump() for e in ai_output.evidence]
        diag.fix_steps_list = ai_output.fix_steps
        diag.limitations_list = ai_output.limitations
        diag.confidence_signals_dict = {
            "ai_confidence": ai_output.confidence,
            "ai_score": ai_output.confidence_score,
            "composite_score": composite_score,
            "rule_agreement": comparison["agreement"],
            "grounding_status": grounding_status,
        }

        db.add(diag)
        db.flush()

        # Step 14: Store rule results
        for r in rule_results:
            rr = RuleResult(
                case_id=case_id,
                diagnosis_id=diag.id,
                rule_name=r.rule_name,
                status=r.status,
                severity=r.severity,
                message=r.message,
            )
            rr.evidence_list = r.evidence
            rr.details_dict = r.details
            db.add(rr)
        db.flush()

        # Step 15: Transition workflow state
        try:
            case_service.transition_state(db, case_id, "AWAITING_HUMAN_REVIEW")
        except Exception:
            # May already be in AWAITING_HUMAN_REVIEW from a previous run
            pass

        # Step 16 & 17: Build response
        diag_response = DiagnosisResponse.from_orm_model(diag)

        return DiagnoseResponse(
            case={"case_id": case.case_id, "category": case.category, "title": case.title},
            ai_diagnosis=diag_response,
            rule_findings=[r.to_dict() for r in rule_results],
            comparison=ComparisonResult(
                agreement=comparison["agreement"],
                agreement_type=comparison["agreement_type"],
                ai_root_cause=comparison["ai_root_cause"],
                rule_findings=comparison["rule_findings"],
                conflicts=comparison["conflicts"],
                grounding_status=grounding_status,
                requires_human_review=True,
            ),
            workflow_state="AWAITING_HUMAN_REVIEW",
            request_id=request_id,
            timestamp=datetime.utcnow(),
        )

    def get_diagnosis(self, db: Session, diagnosis_id: int) -> Diagnosis:
        """Return a diagnosis by ID."""
        d = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
        if not d:
            raise DiagnosisNotFoundError(f"Diagnosis {diagnosis_id} not found.")
        return d

    def get_case_diagnoses(self, db: Session, case_id: str) -> list[Diagnosis]:
        """Return all diagnoses for a case."""
        return (
            db.query(Diagnosis)
            .filter(Diagnosis.case_id == case_id)
            .order_by(Diagnosis.created_at.desc())
            .all()
        )


diagnosis_service = DiagnosisService()
