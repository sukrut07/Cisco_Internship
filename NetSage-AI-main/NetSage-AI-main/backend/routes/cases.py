import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import Case, Diagnosis, RuleCheck, HumanReview
from ..schemas import CaseCreate, CaseResponse, DiagnosisResponse, RuleCheckResponse
from ..rule_checker.checker import DeterministicRuleChecker
from ..ai.engine import get_ai_engine

router = APIRouter(prefix="/api/cases", tags=["cases"])

@router.get("", response_model=List[CaseResponse])
def get_cases(
    concept: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Case)
    if concept and concept.strip():
        query = query.filter(Case.concept == concept)
    if severity and severity.strip():
        query = query.filter(Case.severity == severity)
    if search and search.strip():
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            (Case.title.ilike(search_fmt)) | 
            (Case.symptom.ilike(search_fmt)) | 
            (Case.id.ilike(search_fmt))
        )
    return query.order_by(Case.created_at.desc()).all()


@router.post("", response_model=CaseResponse)
def create_case(case_in: CaseCreate, db: Session = Depends(get_db)):
    case_id = case_in.id or f"CASE-{uuid.uuid4().hex[:6].upper()}"
    
    # Check if ID already exists
    existing = db.query(Case).filter(Case.id == case_id).first()
    if existing:
        case_id = f"CASE-{uuid.uuid4().hex[:6].upper()}"

    db_case = Case(
        id=case_id,
        title=case_in.title,
        symptom=case_in.symptom,
        topology=case_in.topology,
        show_outputs=case_in.show_outputs,
        severity=case_in.severity,
        concept=case_in.concept,
        source_ip=case_in.source_ip,
        dest_ip=case_in.dest_ip,
        subnet_mask=case_in.subnet_mask,
        gateway=case_in.gateway,
        vlan_id=case_in.vlan_id,
        interface=case_in.interface,
        device=case_in.device,
        protocol=case_in.protocol
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Troubleshooting case not found")
    return case


@router.post("/{case_id}/diagnose", response_model=DiagnosisResponse)
def diagnose_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Troubleshooting case not found")

    # Step 1: Run Deterministic Rule Checker
    rule_checker = DeterministicRuleChecker()
    raw_rule_results = rule_checker.analyze(
        show_outputs=case.show_outputs,
        symptom=case.symptom,
        topology=case.topology,
        source_ip=case.source_ip,
        dest_ip=case.dest_ip,
        subnet_mask=case.subnet_mask,
        gateway=case.gateway,
        vlan_id=case.vlan_id
    )

    # Save rule check results into DB
    db.query(RuleCheck).filter(RuleCheck.case_id == case_id).delete()
    for rc in raw_rule_results:
        db_rc = RuleCheck(
            case_id=case_id,
            rule_name=rc["rule"],
            status=rc["status"],
            severity=rc["severity"],
            evidence=rc["evidence"],
            recommendation=rc["recommendation"]
        )
        db.add(db_rc)

    # Step 2: Run AI Diagnosis Engine
    ai_engine = get_ai_engine()
    ai_diag = ai_engine.diagnose(
        title=case.title,
        symptom=case.symptom,
        topology=case.topology,
        show_outputs=case.show_outputs,
        concept=case.concept,
        severity=case.severity,
        rule_checks=raw_rule_results
    )

    # Save Diagnosis into DB
    db_diag = Diagnosis(
        case_id=case_id,
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
    db.refresh(db_diag)

    return DiagnosisResponse(
        id=db_diag.id,
        case_id=case.id,
        root_cause=db_diag.root_cause,
        confidence=db_diag.confidence,
        confidence_level=db_diag.confidence_level,
        osi_layer=db_diag.osi_layer,
        concept=db_diag.concept,
        severity=db_diag.severity,
        evidence=json.loads(db_diag.evidence_json),
        next_commands=json.loads(db_diag.next_commands_json),
        fix_steps=json.loads(db_diag.fix_steps_json),
        alternative_causes=json.loads(db_diag.alternative_causes_json),
        verification_steps=json.loads(db_diag.verification_steps_json),
        created_at=db_diag.created_at
    )


@router.get("/{case_id}/history")
def get_case_history(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    diagnoses = db.query(Diagnosis).filter(Diagnosis.case_id == case_id).order_by(Diagnosis.created_at.desc()).all()
    rule_checks = db.query(RuleCheck).filter(RuleCheck.case_id == case_id).all()
    reviews = db.query(HumanReview).filter(HumanReview.case_id == case_id).order_by(HumanReview.created_at.desc()).all()

    formatted_diagnoses = []
    for d in diagnoses:
        formatted_diagnoses.append({
            "id": d.id,
            "root_cause": d.root_cause,
            "confidence": d.confidence,
            "confidence_level": d.confidence_level,
            "osi_layer": d.osi_layer,
            "concept": d.concept,
            "severity": d.severity,
            "evidence": json.loads(d.evidence_json),
            "next_commands": json.loads(d.next_commands_json),
            "fix_steps": json.loads(d.fix_steps_json),
            "alternative_causes": json.loads(d.alternative_causes_json),
            "verification_steps": json.loads(d.verification_steps_json),
            "created_at": d.created_at
        })

    return {
        "case": case,
        "diagnoses": formatted_diagnoses,
        "rule_checks": [
            {
                "id": rc.id,
                "rule": rc.rule_name,
                "status": rc.status,
                "severity": rc.severity,
                "evidence": rc.evidence,
                "recommendation": rc.recommendation
            } for rc in rule_checks
        ],
        "reviews": reviews
    }
