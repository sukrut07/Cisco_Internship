#!/usr/bin/env python3
"""
NetSage AI — Database Seed Script.

Seeds the database with 35 realistic Cisco network troubleshooting cases.
Run from: backend/
  python scripts/seed_database.py
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import Base, engine, get_db_context
from app.core.logging_config import configure_logging
from app.models import _import_all_models
from app.models.case import Case
from app.models.diagnosis import Diagnosis
from app.models.review import Review
from app.models.verification import Verification
from app.models.rule_result import RuleResult
from app.models.audit import AuditLog
from app.services.audit_service import audit_service
from app.services.diagnosis_service import diagnosis_service
from app.services.review_service import review_service
from app.services.verification_service import verification_service
from app.schemas.review import ReviewCreate, EditedDiagnosis
from app.schemas.verification import VerificationCreate

configure_logging("INFO")
logger = logging.getLogger(__name__)

SEED_FILE = Path(__file__).parent.parent / "data" / "seed_cases.json"


def seed_database() -> None:
    """Seed the database with cases from seed_cases.json and baseline workflow data."""
    # Ensure tables exist
    _import_all_models()
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified.")

    if not SEED_FILE.exists():
        logger.error("Seed file not found: %s", SEED_FILE)
        sys.exit(1)

    with open(SEED_FILE, encoding="utf-8") as f:
        cases_data = json.load(f)

    logger.info("Loaded %d cases from seed file.", len(cases_data))

    created = 0
    skipped = 0

    with get_db_context() as db:
        for raw in cases_data:
            case_id = raw.get("case_id", "").upper()

            if not case_id:
                logger.warning("Skipping case with missing case_id: %s", raw.get("title"))
                skipped += 1
                continue

            # Check for existing case
            existing = db.query(Case).filter(Case.case_id == case_id).first()
            if existing:
                logger.debug("Case %s already exists — skipping.", case_id)
                skipped += 1
                continue

            case = Case(
                case_id=case_id,
                category=raw.get("category", "GENERAL").upper(),
                title=raw.get("title", ""),
                symptom=raw.get("symptom", ""),
                topology=raw.get("topology", ""),
                expected_fault=raw.get("expected_fault"),
                expected_osi_layer=raw.get("expected_osi_layer"),
                concept=raw.get("concept"),
                severity=raw.get("severity", "MEDIUM").upper(),
                next_command=raw.get("next_command"),
                workflow_state="CREATED",
            )
            case.show_outputs_dict = raw.get("show_outputs", {})
            case.expected_fix_list = raw.get("expected_fix", [])
            case.tags_list = raw.get("tags", [])

            db.add(case)
            db.flush()
            created += 1

            audit_service.log(
                db,
                event_type="CASE_CREATED",
                description=f"Case {case_id} initialized from seed catalog.",
                case_id=case_id,
                actor="seed_pipeline",
                metadata={"category": case.category, "severity": case.severity},
            )
            logger.info("Created: %s — %s", case_id, raw.get("title", ""))

    logger.info("Base cases seed complete: %d created, %d skipped.", created, skipped)

    # Seed baseline workflow for key cases to power Dashboard & Responsible AI metrics
    with get_db_context() as db:
        _seed_workflow_samples(db)

    print(f"\nSeed complete: {created} cases created, {skipped} skipped.")
    print("   Run: uvicorn app.main:app --reload")
    print("   Then open: http://localhost:8000/docs")


def _seed_workflow_samples(db, force: bool = False) -> None:
    """Seed sample workflow states for key cases to populate Dashboard & Responsible AI metrics."""
    # Check if we already have sufficient discrepancy reviews
    edited_count = db.query(Review).filter(Review.decision.in_(["EDITED", "REJECTED"])).count()
    if edited_count >= 5 and not force:
        logger.info("Workflow samples already present (%d corrections). Skipping sample seeding.", edited_count)
        return

    logger.info("Seeding realistic sample diagnoses, reviews, and verifications...")

    # Case 4: Hero case (Admin shutdown -> Accepted -> Verified)
    c4 = db.query(Case).filter(Case.case_id == "CASE-004").first()
    if c4:
        diag_resp = diagnosis_service.run_diagnosis(db, "CASE-004")
        diag_id = diag_resp.ai_diagnosis.id
        review = review_service.create_review(
            db,
            "CASE-004",
            ReviewCreate(
                diagnosis_id=diag_id,
                decision="ACCEPTED",
                reviewer="Lead Network Engineer",
                review_reason="AI diagnosis matches interface state exactly.",
                review_notes="Verified against show ip interface brief.",
            ),
        )
        review_service.record_fix(
            db,
            "CASE-004",
            review.id,
            commands=["configure terminal", "interface GigabitEthernet0/1", "no shutdown", "end"],
            description="Re-enabled administratively shut down interface Gi0/1 on R1.",
            performed_by="Lead Network Engineer",
        )
        verification_service.create_verification(
            db,
            "CASE-004",
            VerificationCreate(
                review_id=review.id,
                verification_status="SUCCESS",
                verification_method="PING",
                verification_evidence="5/5 ICMP echo replies received from PC1 to Server1 (10.0.0.100).",
                verified_by="Lead Network Engineer",
            ),
        )

    # Discrepancy Case 1: CASE-003 (Duplicate IP - Human EDITED)
    c3 = db.query(Case).filter(Case.case_id == "CASE-003").first()
    if c3:
        diag_resp = diagnosis_service.run_diagnosis(db, "CASE-003")
        review = review_service.create_review(
            db,
            "CASE-003",
            ReviewCreate(
                diagnosis_id=diag_resp.ai_diagnosis.id,
                decision="EDITED",
                reviewer="Network Operations Specialist",
                review_reason="AI prioritized interface flap counter over secondary ARP entry with duplicate MAC address.",
                review_notes="Static IP collision between PC1 and rogue printer.",
                edited_diagnosis=EditedDiagnosis(
                    root_cause="Duplicate IP address assigned to rogue device on subnet, conflicting with PC1 gateway ARP entry.",
                    confidence="HIGH",
                    confidence_score=0.92,
                    evidence=[{"source_command": "show ip arp", "snippet": "duplicate IP 192.168.1.10 detected with alternate MAC"}],
                    osi_layer="Layer 3 - Network",
                    next_command="show arp",
                    fix_steps=["Re-assign unique static IP or configure DHCP reservation on rogue device."],
                ),
            ),
        )
        review_service.record_fix(
            db,
            "CASE-003",
            review.id,
            commands=["interface Gi0/2", "shutdown"],
            description="Disabled conflicting switchport to isolate duplicate MAC address.",
            performed_by="Network Operations Specialist",
        )
        verification_service.create_verification(
            db,
            "CASE-003",
            VerificationCreate(
                review_id=review.id,
                verification_status="SUCCESS",
                verification_method="PING",
                verification_evidence="Duplicate IP warning cleared. PC1 ping success rate 100%.",
                verified_by="Network Operations Specialist",
            ),
        )

    # Discrepancy Case 2: CASE-009 (ACL Blocking vs Missing Route - Human EDITED)
    c9 = db.query(Case).filter(Case.case_id == "CASE-009").first()
    if c9:
        diag_resp = diagnosis_service.run_diagnosis(db, "CASE-009")
        review = review_service.create_review(
            db,
            "CASE-009",
            ReviewCreate(
                diagnosis_id=diag_resp.ai_diagnosis.id,
                decision="EDITED",
                reviewer="Security Engineer",
                review_reason="AI flagged ACL deny statement, but routing table had no route to destination network.",
                review_notes="Missing static route prevented traffic before ACL evaluation.",
                edited_diagnosis=EditedDiagnosis(
                    root_cause="Missing static route to destination subnet 192.168.30.0/24 on gateway router.",
                    confidence="HIGH",
                    confidence_score=0.95,
                    evidence=[{"source_command": "show ip route", "snippet": "192.168.30.0/24 subnet absent from FIB"}],
                    osi_layer="Layer 3 - Network",
                    next_command="show ip route 192.168.30.0",
                    fix_steps=["ip route 192.168.30.0 255.255.255.0 10.0.0.2"],
                ),
            ),
        )

    # Discrepancy Case 3: CASE-012 (MTU Mismatch - Human REJECTED)
    c12 = db.query(Case).filter(Case.case_id == "CASE-012").first()
    if c12:
        diag_resp = diagnosis_service.run_diagnosis(db, "CASE-012")
        review_service.create_review(
            db,
            "CASE-012",
            ReviewCreate(
                diagnosis_id=diag_resp.ai_diagnosis.id,
                decision="REJECTED",
                reviewer="Core Network Architect",
                review_reason="AI recommended 'ip ospf mtu-ignore', which would mask fragmentation packet drops in production.",
                review_notes="Rejected recommendation in favor of fixing physical MTU mismatch.",
            ),
        )

    # Discrepancy Case 4: CASE-018 (DHCP Pool Exhaustion vs VLAN Mismatch - Human EDITED)
    c18 = db.query(Case).filter(Case.case_id == "CASE-018").first()
    if c18:
        diag_resp = diagnosis_service.run_diagnosis(db, "CASE-018")
        review = review_service.create_review(
            db,
            "CASE-018",
            ReviewCreate(
                diagnosis_id=diag_resp.ai_diagnosis.id,
                decision="EDITED",
                reviewer="Site Support Tech",
                review_reason="AI suspected DHCP pool exhaustion, but access switchport was placed in incorrect VLAN.",
                review_notes="Port assigned to VLAN 99 instead of client VLAN 10.",
                edited_diagnosis=EditedDiagnosis(
                    root_cause="Access switchport FastEthernet0/5 configured for dead VLAN 99 instead of data VLAN 10.",
                    confidence="HIGH",
                    confidence_score=0.90,
                    evidence=[{"source_command": "show vlan brief", "snippet": "Fa0/5 assigned to VLAN 99 (Isolated)"}],
                    osi_layer="Layer 2 - Data Link",
                    next_command="show interfaces Fa0/5 switchport",
                    fix_steps=["interface Fa0/5", "switchport access vlan 10"],
                ),
            ),
        )

    # Discrepancy Case 5: CASE-022 (DNS vs Default Gateway - Human EDITED)
    c22 = db.query(Case).filter(Case.case_id == "CASE-022").first()
    if c22:
        diag_resp = diagnosis_service.run_diagnosis(db, "CASE-022")
        review_service.create_review(
            db,
            "CASE-022",
            ReviewCreate(
                diagnosis_id=diag_resp.ai_diagnosis.id,
                decision="EDITED",
                reviewer="Network Lead",
                review_reason="AI identified DNS timeout, but root cause is default gateway route missing on core switch.",
                review_notes="Without default gateway 0.0.0.0/0, DNS queries cannot leave the local network segment.",
                edited_diagnosis=EditedDiagnosis(
                    root_cause="Default gateway route 0.0.0.0/0 missing on Core Switch S1.",
                    confidence="HIGH",
                    confidence_score=0.94,
                    evidence=[{"source_command": "show ip route", "snippet": "Gateway of last resort is not set"}],
                    osi_layer="Layer 3 - Network",
                    next_command="show ip route",
                    fix_steps=["ip route 0.0.0.0 0.0.0.0 192.168.1.1"],
                ),
            ),
        )

    # Clean Accepted Cases: CASE-001, CASE-002, CASE-005, CASE-006, CASE-007
    for cid in ["CASE-001", "CASE-002", "CASE-005", "CASE-006", "CASE-007"]:
        c = db.query(Case).filter(Case.case_id == cid).first()
        if c:
            diag_resp = diagnosis_service.run_diagnosis(db, cid)
            review = review_service.create_review(
                db,
                cid,
                ReviewCreate(
                    diagnosis_id=diag_resp.ai_diagnosis.id,
                    decision="ACCEPTED",
                    reviewer="Senior Network Engineer",
                    review_reason="Root cause and evidence verified.",
                ),
            )
            review_service.record_fix(
                db,
                cid,
                review.id,
                commands=c.expected_fix_list or ["configure terminal"],
                description=f"Applied fix for {cid}.",
                performed_by="Senior Network Engineer",
            )
            verification_service.create_verification(
                db,
                cid,
                VerificationCreate(
                    review_id=review.id,
                    verification_status="SUCCESS",
                    verification_method="SHOW_COMMAND",
                    verification_evidence="Verification tests passed.",
                    verified_by="Senior Network Engineer",
                ),
            )

    logger.info("Sample workflow seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
