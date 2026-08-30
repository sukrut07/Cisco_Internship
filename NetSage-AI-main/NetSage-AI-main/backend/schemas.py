from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class CaseBase(BaseModel):
    title: str
    symptom: str
    topology: str
    show_outputs: str
    severity: str = "Medium"
    concept: str = "Routing"
    
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    subnet_mask: Optional[str] = None
    gateway: Optional[str] = None
    vlan_id: Optional[int] = None
    interface: Optional[str] = None
    device: Optional[str] = None
    protocol: Optional[str] = None

class CaseCreate(CaseBase):
    id: Optional[str] = None

class CaseResponse(CaseBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class DiagnosisResponse(BaseModel):
    id: Optional[int] = None
    case_id: str
    root_cause: str
    confidence: int
    confidence_level: str
    osi_layer: str
    concept: str
    severity: str
    evidence: List[str]
    next_commands: List[str]
    fix_steps: List[str]
    alternative_causes: List[str]
    verification_steps: List[str]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RuleCheckResponse(BaseModel):
    id: Optional[int] = None
    case_id: Optional[str] = None
    rule: str
    status: str
    severity: str
    evidence: str
    recommendation: str

    class Config:
        from_attributes = True


class HumanReviewCreate(BaseModel):
    decision: str  # ACCEPT, EDIT, REJECT
    corrected_root_cause: Optional[str] = None
    corrected_osi_layer: Optional[str] = None
    corrected_explanation: Optional[str] = None
    corrected_fix: Optional[str] = None
    reviewer_comments: Optional[str] = None
    reviewer_name: str = "Network Engineer"

class HumanReviewResponse(BaseModel):
    id: int
    case_id: str
    diagnosis_id: Optional[int]
    decision: str
    corrected_root_cause: Optional[str]
    corrected_osi_layer: Optional[str]
    corrected_explanation: Optional[str]
    corrected_fix: Optional[str]
    reviewer_comments: Optional[str]
    reviewer_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class VerificationCreate(BaseModel):
    verification_output: str

class VerificationResponse(BaseModel):
    id: int
    case_id: str
    verification_output: str
    status: str
    explanation: str
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_cases: int
    accepted_diagnoses: int
    edited_diagnoses: int
    rejected_diagnoses: int
    agreement_rate: float
    correction_count: int
    
    by_concept: Dict[str, int]
    by_severity: Dict[str, int]
    by_osi_layer: Dict[str, int]
    recent_cases: List[CaseResponse]


class ResponsibleAILogItem(BaseModel):
    case_id: str
    case_title: str
    original_ai_diagnosis: str
    human_correction: str
    reason_for_correction: str
    date: str
    reviewer: str
    final_diagnosis: str
    decision: str
