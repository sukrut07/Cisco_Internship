import csv
import os
import json
import datetime
from sqlalchemy.orm import Session
from backend.database import engine, Base, SessionLocal
from backend.models import Case, Diagnosis, RuleCheck, HumanReview, Verification
from backend.rule_checker.checker import DeterministicRuleChecker
from backend.ai.engine import get_ai_engine

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "cases.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join("data", "cases.csv")
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    print("Seeding cases from CSV...")
    cases_count = 0
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            case_id = row["case_id"]
            existing = db.query(Case).filter(Case.id == case_id).first()
            if not existing:
                db_case = Case(
                    id=case_id,
                    title=row["title"],
                    symptom=row["symptom"],
                    topology=row["topology"],
                    show_outputs=row["show_outputs"],
                    severity=row["severity"],
                    concept=row["concept"]
                )
                db.add(db_case)
                cases_count += 1

    db.commit()
    print(f"Seeded {cases_count} cases into database.")

    # Now generate diagnoses, rule checks, and human review logs for sample cases
    all_cases = db.query(Case).all()
    rule_checker = DeterministicRuleChecker()
    ai_engine = get_ai_engine()

    for case in all_cases:
        # Run rule checker
        rc_results = rule_checker.analyze(
            show_outputs=case.show_outputs,
            symptom=case.symptom,
            topology=case.topology
        )
        db.query(RuleCheck).filter(RuleCheck.case_id == case.id).delete()
        for r in rc_results:
            db_rc = RuleCheck(
                case_id=case.id,
                rule_name=r["rule"],
                status=r["status"],
                severity=r["severity"],
                evidence=r["evidence"],
                recommendation=r["recommendation"]
            )
            db.add(db_rc)

        # Generate diagnosis if none exists
        existing_diag = db.query(Diagnosis).filter(Diagnosis.case_id == case.id).first()
        if not existing_diag:
            ai_diag = ai_engine.diagnose(
                title=case.title,
                symptom=case.symptom,
                topology=case.topology,
                show_outputs=case.show_outputs,
                concept=case.concept,
                severity=case.severity,
                rule_checks=rc_results
            )
            db_diag = Diagnosis(
                case_id=case.id,
                root_cause=ai_diag["root_cause"],
                confidence=ai_diag["confidence"],
                confidence_level=ai_diag["confidence_level"],
                osi_layer=ai_diag["osi_layer"],
                concept=ai_diag.get("concept", case.concept),
                severity=ai_diag.get("severity", case.severity),
                evidence_json=json.dumps(ai_diag.get("evidence", [])),
                next_commands_json=json.dumps(ai_diag.get("next_commands", [])),
                fix_steps_json=json.dumps(ai_diag.get("fix_steps", [])),
                alternative_causes_json=json.dumps(ai_diag.get("alternative_causes", [])),
                verification_steps_json=json.dumps(ai_diag.get("verification_steps", []))
            )
            db.add(db_diag)

    db.commit()

    # Create Responsible AI seed reviews (at least 5 corrected cases + accepted cases)
    sample_reviews = [
        {
            "case_id": "CASE-101",
            "decision": "ACCEPT",
            "reviewer_comments": "Concur with AI diagnosis. VLAN 30 database entry is missing on Switch-2.",
            "reviewer_name": "Marcus Vance (CCIE #54210)"
        },
        {
            "case_id": "CASE-102",
            "decision": "EDIT",
            "corrected_root_cause": "Default gateway configured on PC-1 (192.168.2.1) is outside local subnet 192.168.1.0/24.",
            "corrected_osi_layer": "Layer 3 (Network)",
            "corrected_explanation": "AI identified gateway mismatch but missed subinterface Fa0/0.1 routing table entry detail.",
            "corrected_fix": "Change PC-1 Gateway to 192.168.1.1 and verify ARP resolution.",
            "reviewer_comments": "Refined root cause explanation to specify exact subinterface IP.",
            "reviewer_name": "Elena Rostova (Lead NetEng)"
        },
        {
            "case_id": "CASE-103",
            "decision": "ACCEPT",
            "reviewer_comments": "Confirmed ip helper-address is missing on router subinterface Fa0/0.20.",
            "reviewer_name": "Marcus Vance (CCIE #54210)"
        },
        {
            "case_id": "CASE-104",
            "decision": "EDIT",
            "corrected_root_cause": "Host DNS server IP (10.0.0.55) is unreachable due to missing routing table entry for host route /32.",
            "corrected_osi_layer": "Layer 7 (Application)",
            "corrected_explanation": "AI flagged DNS IP typo, but primary root cause is DNS Server IP 10.0.0.55 being unreachable on the network.",
            "corrected_fix": "Reconfigure host DNS to 10.0.0.53 and add static route on Router.",
            "reviewer_comments": "Updated OSI layer focus to DNS Application Layer.",
            "reviewer_name": "Sarah Jenkins (Senior NetEng)"
        },
        {
            "case_id": "CASE-105",
            "decision": "REJECT",
            "reviewer_comments": "AI suggested physical layer failure, but static route points to incorrect next-hop IP 192.168.12.6 instead of 192.168.12.2.",
            "reviewer_name": "Sarah Jenkins (Senior NetEng)"
        },
        {
            "case_id": "CASE-106",
            "decision": "EDIT",
            "corrected_root_cause": "ACL 101 rule 10 explicitly drops IP traffic to DMZ host before rule 20 permits TCP port 80.",
            "corrected_osi_layer": "Layer 4 (Transport)",
            "corrected_explanation": "AI identified ACL block but didn't highlight line rule sequence order precedence.",
            "corrected_fix": "Reorder ACL: delete line 10 or permit tcp port 80 prior to explicit deny rule.",
            "reviewer_comments": "Fixed ACL sequence order suggestion.",
            "reviewer_name": "Elena Rostova (Lead NetEng)"
        },
        {
            "case_id": "CASE-107",
            "decision": "EDIT",
            "corrected_root_cause": "Interface GigabitEthernet0/0/0 missing 'ip nat inside' statement.",
            "corrected_osi_layer": "Layer 3 (Network)",
            "corrected_explanation": "AI diagnosed NAT pool misconfiguration, but interface binding command was missing.",
            "corrected_fix": "Execute 'interface GigabitEthernet0/0/0' followed by 'ip nat inside'.",
            "reviewer_comments": "Corrected command syntax to ip nat inside.",
            "reviewer_name": "Marcus Vance (CCIE #54210)"
        },
        {
            "case_id": "CASE-108",
            "decision": "REJECT",
            "reviewer_comments": "AI diagnosed AP power supply failure, but WLC log explicitly shows RADIUS Shared Secret Mismatch.",
            "reviewer_name": "David Kim (Wireless Architect)"
        }
    ]

    for sr in sample_reviews:
        case_id = sr["case_id"]
        existing_rev = db.query(HumanReview).filter(HumanReview.case_id == case_id).first()
        if not existing_rev:
            diag = db.query(Diagnosis).filter(Diagnosis.case_id == case_id).order_by(Diagnosis.created_at.desc()).first()
            db_rev = HumanReview(
                case_id=case_id,
                diagnosis_id=diag.id if diag else None,
                decision=sr["decision"],
                corrected_root_cause=sr.get("corrected_root_cause"),
                corrected_osi_layer=sr.get("corrected_osi_layer"),
                corrected_explanation=sr.get("corrected_explanation"),
                corrected_fix=sr.get("corrected_fix"),
                reviewer_comments=sr.get("reviewer_comments"),
                reviewer_name=sr.get("reviewer_name")
            )
            db.add(db_rev)

    db.commit()
    print("Database successfully seeded with cases, rule checks, AI diagnoses, and human review logs!")

if __name__ == "__main__":
    seed_database()
