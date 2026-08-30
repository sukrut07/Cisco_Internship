# NetSage AI — Repository Audit & Requirements Assessment

**Project:** NetSage AI (Applied AI + Network Troubleshooting)  
**Track:** Cisco-AICTE Virtual Internship Program (VIP 2026)  
**Date:** August 2026  
**Auditor:** Automated Diagnostic System  

---

## 1. Executive Summary

A comprehensive audit was performed across the NetSage AI codebase. The repository contains a production-grade FastAPI backend and React 19 + Tailwind CSS frontend with a deterministic multi-layer rule engine (L1–L7), AI grounding pipeline, human review gateway, and an immutable audit trail. 126 automated backend unit and integration tests are passing.

This audit evaluates the codebase against the official **Cisco-AICTE VIP 2026 Problem Statement** and the **3-file submission constraint** established by the evaluation committee.

---

## 2. Existing Architecture & Components

```
                                  ┌───────────────────────────┐
                                  │      React 19 Frontend    │
                                  │   (Vite + Tailwind Glass) │
                                  └─────────────┬─────────────┘
                                                │ HTTP / REST
                                  ┌─────────────▼─────────────┐
                                  │    FastAPI Gateway API    │
                                  └──────┬─────────────┬──────┘
                                         │             │
                    ┌────────────────────▼────┐   ┌────▼─────────────────────┐
                    │ Deterministic Rule      │   │ Multi-Provider AI        │
                    │ Engine (11 L1-L7 Rules) │   │ Grounding & Parser       │
                    └────────────────────┬────┘   └────┬─────────────────────┘
                                         │             │
                                  ┌──────▼─────────────▼──────┐
                                  │ Hybrid Comparison Engine  │
                                  │   (Agreement / Conflict)  │
                                  └─────────────┬─────────────┘
                                                │
                                  ┌─────────────▼─────────────┐
                                  │ MANDATORY HUMAN GATEWAY   │
                                  │ (ACCEPTED/EDITED/REJECTED)│
                                  └─────────────┬─────────────┘
                                                │
                                  ┌─────────────▼─────────────┐
                                  │ Post-Fix Verification     │
                                  │ & Immutable Audit Trail   │
                                  └───────────────────────────┘
```

### Component Status Matrix

| Component | Status | Details |
|---|---|---|
| **Backend API** | ✅ Fully Functional | FastAPI 0.115+, SQLAlchemy 2.0, Pydantic v2 schemas, REST endpoints for cases, evidence, diagnoses, reviews, fixes, verification, dashboard, responsible AI, and audit. |
| **Deterministic Rule Engine** | ✅ Fully Functional | 11 protocol rules covering duplicate IP, subnet masks, gateway mismatches, admin shutdown, VLAN creation/native mismatch, static/dynamic routes, trunking, ACL deny filters, NAT translations, DHCP snooping/pools, and DNS resolution. |
| **AI Grounding Engine** | ✅ Fully Functional | Multi-provider support (Mock, Gemini, OpenAI, Claude) with anti-hallucination citation parser extracting exact telemetry line numbers and evidence verification. |
| **Human Review Gateway** | ✅ Fully Functional | Strict `ACCEPTED`, `EDITED`, `REJECTED` enforcement. Disallows automated fixing without human approval. |
| **Audit Ledger** | ✅ Fully Functional | Append-only event logging tracking case creation, AI diagnoses, human reviews, fix application, and verification tests. |
| **Frontend Application** | ✅ Fully Functional | React 19 + Vite dashboard featuring telemetry charts, interactive case explorer, confidence gauges, live review workflow modal, and responsible AI discrepancy ledger. |
| **Seed Dataset** | ✅ Present (35 Cases) | 35 structured troubleshooting cases covering all required network domains in `backend/data/seed_cases.json`. |
| **Test Suite** | ✅ 126/126 Passing | Comprehensive pytest suite verifying API endpoints, rule execution, parser edge cases, review transitions, and grounding logic. |

---

## 3. Cisco-AICTE VIP 2026 Requirements Mapping

| VIP 2026 Deliverable | Requirement | Current Status | Action Required |
|---|---|---|---|
| **Dataset (`cases.csv`)** | ≥30 cases with symptoms, topology, show commands, expected fault, OSI layer, concept, severity, and evidence | Partial (Present as JSON, missing CSV export at root/dataset) | Generate `cases.csv` and `dataset/cases.csv` with full 35-case metadata. |
| **AI Prompt System** | `diagnose_prompt.md` with strict JSON schema, evidence grounding, next command, confidence score, and 2–3 worked examples | Partial (Present in backend, requires update for schema parity & root location) | Create root `prompts/diagnose_prompt.md` with complete 12-field schema and 3 worked examples. |
| **Python Rule Checker** | Deterministic Python validator checking duplicate IP, wrong mask, gateway mismatch, interface shutdown, missing VLAN, missing route | Present in `backend/app/rules/` | Create standalone CLI module `checker/rule_checker.py` callable independently of web server. |
| **Human Oversight Gate** | Mandatory human review (`ACCEPTED`, `EDITED`, `REJECTED`); no auto-fixing | Implemented in backend & UI | Standardize CSV review export in `responsible_ai/review_log.csv`. |
| **Responsible AI Log** | ≥5 documented cases where human corrected AI with technical explanations | Implemented in seed data | Export dedicated ledger in `responsible_ai/review_log.csv` and document in report. |
| **Dashboard** | KPI cards & charts showing issue types, severity, OSI layer, and AI-vs-human agreement | Implemented in React frontend & API | Document metrics and spreadsheet format for evaluation package. |
| **Packet Tracer Sample** | Representative `.pkt` scenario (Inter-VLAN routing) with broken/fixed states and CLI outputs | Missing manual `.pkt` instructions & structured folder | Create `packet_tracer/` structure, CLI configs, broken/fixed states, and step-by-step human guide. |
| **Project Report** | Comprehensive technical report covering all 25 problem statement sections | Missing final markdown draft | Create `docs/NetSageAI_Project_Report.md`. |
| **Demo Video Script** | 5–10 minute script showing broken lab → diagnosis → review → fix → verify | Missing formal script | Create `docs/DEMO_SCRIPT.md`. |
| **Submission Package** | Max 3 files in ZIP (Report PDF, Sample `.pkt`, Source Code ZIP) | Missing checklist | Create `submission/SUBMISSION_CHECKLIST.md`. |

---

## 4. Preservation & Non-Regression Directives

1. **Do NOT rewrite existing backend logic**: The FastAPI server, models, database layer, and React frontend are fully working with 126 passing tests.
2. **Do NOT generate fake `.pkt` binaries**: Packet Tracer `.pkt` files are binary Cisco proprietary formats. Fabricating binary files will cause corrupt file errors during evaluation. Prepare exact Cisco CLI configurations, topology diagrams, and setup instructions instead.
3. **Keep modularity**: Standalone scripts (such as `checker/rule_checker.py` and `backend/scripts/seed_database.py`) must function independently.
