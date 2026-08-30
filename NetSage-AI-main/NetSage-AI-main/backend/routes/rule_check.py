from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..models import Case, RuleCheck
from ..schemas import RuleCheckResponse
from ..rule_checker.checker import DeterministicRuleChecker

router = APIRouter(prefix="/api/cases", tags=["rule_check"])

class RawRuleCheckInput(BaseModel):
    show_outputs: str
    symptom: Optional[str] = ""
    topology: Optional[str] = ""
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    subnet_mask: Optional[str] = None
    gateway: Optional[str] = None
    vlan_id: Optional[int] = None

@router.post("/{case_id}/rule-check", response_model=List[RuleCheckResponse])
def run_case_rule_check(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    checker = DeterministicRuleChecker()
    results = checker.analyze(
        show_outputs=case.show_outputs,
        symptom=case.symptom,
        topology=case.topology,
        source_ip=case.source_ip,
        dest_ip=case.dest_ip,
        subnet_mask=case.subnet_mask,
        gateway=case.gateway,
        vlan_id=case.vlan_id
    )

    db.query(RuleCheck).filter(RuleCheck.case_id == case_id).delete()
    db_results = []
    for rc in results:
        db_rc = RuleCheck(
            case_id=case_id,
            rule_name=rc["rule"],
            status=rc["status"],
            severity=rc["severity"],
            evidence=rc["evidence"],
            recommendation=rc["recommendation"]
        )
        db.add(db_rc)
        db_results.append(db_rc)

    db.commit()
    for db_rc in db_results:
        db.refresh(db_rc)

    return [
        RuleCheckResponse(
            id=r.id,
            case_id=r.case_id,
            rule=r.rule_name,
            status=r.status,
            severity=r.severity,
            evidence=r.evidence,
            recommendation=r.recommendation
        ) for r in db_results
    ]


@router.post("/rule-check/sandbox", response_model=List[RuleCheckResponse])
def run_raw_rule_check(input_data: RawRuleCheckInput):
    checker = DeterministicRuleChecker()
    results = checker.analyze(
        show_outputs=input_data.show_outputs,
        symptom=input_data.symptom or "",
        topology=input_data.topology or "",
        source_ip=input_data.source_ip,
        dest_ip=input_data.dest_ip,
        subnet_mask=input_data.subnet_mask,
        gateway=input_data.gateway,
        vlan_id=input_data.vlan_id
    )

    return [
        RuleCheckResponse(
            rule=r["rule"],
            status=r["status"],
            severity=r["severity"],
            evidence=r["evidence"],
            recommendation=r["recommendation"]
        ) for r in results
    ]
