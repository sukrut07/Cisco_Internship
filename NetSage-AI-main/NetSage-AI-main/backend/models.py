import datetime
import json
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from .database import Base

class Case(Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    symptom = Column(Text, nullable=False)
    topology = Column(Text, nullable=False)
    show_outputs = Column(Text, nullable=False)
    severity = Column(String, default="Medium")
    concept = Column(String, default="Routing")
    
    # Optional structured metadata
    source_ip = Column(String, nullable=True)
    dest_ip = Column(String, nullable=True)
    subnet_mask = Column(String, nullable=True)
    gateway = Column(String, nullable=True)
    vlan_id = Column(Integer, nullable=True)
    interface = Column(String, nullable=True)
    device = Column(String, nullable=True)
    protocol = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    diagnoses = relationship("Diagnosis", back_populates="case", cascade="all, delete-orphan")
    rule_checks = relationship("RuleCheck", back_populates="case", cascade="all, delete-orphan")
    reviews = relationship("HumanReview", back_populates="case", cascade="all, delete-orphan")
    verifications = relationship("Verification", back_populates="case", cascade="all, delete-orphan")


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    root_cause = Column(Text, nullable=False)
    confidence = Column(Integer, default=80)
    confidence_level = Column(String, default="High")
    osi_layer = Column(String, default="Layer 3 (Network)")
    concept = Column(String, default="Routing")
    severity = Column(String, default="Medium")
    
    # Stored as JSON strings
    evidence_json = Column(Text, default="[]")
    next_commands_json = Column(Text, default="[]")
    fix_steps_json = Column(Text, default="[]")
    alternative_causes_json = Column(Text, default="[]")
    verification_steps_json = Column(Text, default="[]")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    case = relationship("Case", back_populates="diagnoses")
    reviews = relationship("HumanReview", back_populates="diagnosis")


class RuleCheck(Base):
    __tablename__ = "rule_checks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    rule_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # passed / failed
    severity = Column(String, default="low")
    evidence = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    case = relationship("Case", back_populates="rule_checks")


class HumanReview(Base):
    __tablename__ = "human_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    diagnosis_id = Column(Integer, ForeignKey("diagnoses.id"), nullable=True)
    decision = Column(String, nullable=False)  # ACCEPT, EDIT, REJECT
    
    corrected_root_cause = Column(Text, nullable=True)
    corrected_osi_layer = Column(String, nullable=True)
    corrected_explanation = Column(Text, nullable=True)
    corrected_fix = Column(Text, nullable=True)
    reviewer_comments = Column(Text, nullable=True)
    reviewer_name = Column(String, default="Senior NetEng Reviewer")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    case = relationship("Case", back_populates="reviews")
    diagnosis = relationship("Diagnosis", back_populates="reviews")


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    verification_output = Column(Text, nullable=False)
    status = Column(String, nullable=False)  # Passed / Failed
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    case = relationship("Case", back_populates="verifications")
