# NetSage AI — AI-Powered Cisco Network Troubleshooting Assistant

NetSage AI is an enterprise-grade AI-assisted network troubleshooting application for Cisco-style networking labs and Cisco Packet Tracer scenarios.

It combines **deterministic Python rule checking** with **structured AI diagnosis**, governed strictly by **human-in-the-loop oversight** and **responsible AI audit logging**.

---

## 🌟 Key Features

1. **Deterministic Python Rule Checker**:
   - Hardcoded, zero-hallucination pre-checks for:
     - **Duplicate IP** address conflicts (`%IP-4-DUPADDR`)
     - **Gateway Mismatch** (Host IP vs Subnet Gateway)
     - **Interface Down** (`administratively down`, `line protocol is down`, `err-disabled`)
     - **Missing VLAN** (`VLAN inactive`, missing global database entry)
     - **Missing Route** (`Gateway of last resort is not set`, RIB lookup failure)
     - **Wrong Subnet Mask** (Prefix boundary mismatch)

2. **Structured AI Diagnosis Engine**:
   - Adheres strictly to JSON Schema in `prompts/diagnose_prompt.md`.
   - Supports live Gemini/OpenAI API via `AI_API_KEY`.
   - Built-in **Mock AI Engine** for seamless local execution without requiring API keys.

3. **Human-in-the-Loop Review System**:
   - Diagnoses are **never** treated as final authority.
   - Engineers can:
     - **ACCEPT**: Approve AI diagnosis.
     - **EDIT**: Correct root cause, OSI layer, fix steps, or rationale.
     - **REJECT**: Reject diagnosis with required technical comments.

4. **Responsible AI Audit Log**:
   - Tracks human corrections and overrides.
   - Calculates **AI-Human Agreement Rate (%)** and **AI Correction Rate (%)**.

5. **Post-Fix Verification Engine**:
   - Evaluates post-fix CLI show commands and ping outputs, displaying **Verification Passed** or **Verification Failed**.

6. **30 Realistic Packet Tracer Lab Dataset**:
   - Pre-seeded dataset spanning VLAN, Gateway, DHCP, DNS, Routing, ACL, NAT, and Wireless.

---

## 🏗️ Architecture Overview

```
User Scenario Input (Symptoms, Topology, Show Outputs)
                        ↓
               FastAPI Backend API
                        ↓
    Deterministic Rule Checker  +  AI Diagnosis Engine (Live / Mock)
                        ↓                      ↓
             Rule Check Findings         AI Suggested Diagnosis (JSON)
                        ↘                      ↙
                         Combined Evidence View
                                    ↓
                        Human Review Dashboard
                       (ACCEPT / EDIT / REJECT)
                                    ↓
                     Database Audit & Verification
                                    ↓
                 Analytics Dashboard & Responsible AI Log
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.10+
- Node.js v18+ & npm

### 1. Install Backend Dependencies & Seed Database

```bash
# Install Python requirements
pip install -r requirements.txt

# Initialize & seed 30 Packet Tracer cases + Responsible AI logs
python -m backend.seed
```

### 2. Run Backend API Server

```bash
python -m uvicorn backend.main:app --reload --port 8000
```
Backend API docs available at: `http://localhost:8000/docs`

### 3. Run Frontend Web Application

```bash
cd frontend
npm install
npm run dev
```
Open application in browser: `http://localhost:5173/`

---

## 🔑 Environment Variables & AI Configuration

Create a `.env` file in the root directory if using live AI models:

```env
# Optional: OpenAI / Gemini API Key
AI_API_KEY=your_actual_api_key_here

# Optional: Database Connection String (Defaults to SQLite sqlite:///./netsage.db)
DATABASE_URL=sqlite:///./netsage.db
```

*Note: If `AI_API_KEY` is omitted, NetSage AI operates automatically in Demo Mode using the built-in Mock Diagnosis Engine.*

---

## 🧪 Running Automated Tests

Run backend unit and integration test suite:

```bash
python -m pytest tests/
```

---

## 📂 Project Structure

```
NetSage AI/
├── prompts/
│   └── diagnose_prompt.md          # Cisco System Prompt & JSON Schema
├── data/
│   ├── generate_cases.py           # Dataset generator script
│   └── cases.csv                   # 30 Cisco Packet Tracer troubleshooting cases
├── backend/
│   ├── main.py                     # FastAPI application entry point
│   ├── database.py                 # SQLAlchemy DB configuration
│   ├── models.py                   # Case, Diagnosis, RuleCheck, HumanReview, Verification models
│   ├── schemas.py                  # Pydantic schemas
│   ├── seed.py                     # Seeder script
│   ├── rule_checker/               # Deterministic Python rule checker
│   ├── ai/                         # Abstract AI Engine & Mock Engine
│   └── routes/                     # API endpoint routers
├── frontend/                       # Vite React application
│   ├── src/
│   │   ├── components/             # Reusable UI components
│   │   ├── pages/                  # Dashboard, NewCase, CaseDetail, ResponsibleAILog, etc.
│   │   └── services/               # Axios API client
│   └── index.css                   # Cisco dark telemetry design system
├── tests/                          # Pytest test suite
├── requirements.txt
└── README.md
```
