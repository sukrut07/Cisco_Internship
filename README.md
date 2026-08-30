# NetSage-AI
> **Autonomous Network Monitoring & Intelligent Traffic Analytics Platform with Deterministic Layer 1–7 Rule Checking and Mandatory Human-in-the-Loop Review.**

[![CI/CD Tests](https://img.shields.io/badge/Tests-126%2F126%20Passed-brightgreen)](https://github.com/sukrut07/Cisco_Internship)
[![Quality Gate](https://img.shields.io/badge/Quality%20Gate-17%2F17%20Verified-blue)](https://github.com/sukrut07/Cisco_Internship)
[![Track](https://img.shields.io/badge/Cisco--AICTE%20VIP-2026-orange)](https://github.com/sukrut07/Cisco_Internship)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Cisco-AICTE Virtual Internship Program (VIP 2026) — Project 2 (Applied AI + Network Troubleshooting)**  
**Author:** Sukrut Dusane (`sukrut07`)

---

## 1. System Overview

**NetSage-AI** is an autonomous network monitoring and intelligent traffic analytics platform that bridges simulated Cisco network infrastructure with data-driven anomaly detection and grounded AI troubleshooting.

Built upon an enterprise dual-subnet topology (`Netsage-Gateway`, `NetSage_AI_Server` at `192.168.1.10`, `Admin-PC` at `192.168.2.10`, and `Client-PC1` at `192.168.2.20`) with integrated DNS (`netsage.ai`) and HTTP management services, NetSage-AI combines:

1. **Deterministic Rule Engine (Layer 1–7):** 11 protocol checks (interface state, duplicate IP, subnet masks, default gateways, static/dynamic routing, VLAN trunking, ACL deny filters, NAT translations, DHCP snooping/pools, and DNS resolution).
2. **Multi-Provider AI Grounding Engine:** Supports Mock, OpenAI, Google Gemini, and Anthropic Claude with strict anti-hallucination citation parsing against Cisco `show` command outputs.
3. **Mandatory Human-in-the-Loop Review Gate:** AI provides diagnostic recommendations and stages CLI remediation commands; authorized human engineers must explicitly review (`ACCEPTED`, `EDITED`, or `REJECTED`) before fix staging or verification.
4. **Immutable Audit Trail:** Append-only cryptographic-style audit logging for compliance, review traceability, and prompt recalibration.
5. **Modern Glassmorphism Frontend:** High-performance React 19 + Vite dashboard featuring real-time diagnostic telemetry, live topology inspection, confidence gauges, and responsible AI discrepancy ledger.

```
                ┌────────────────────────────────────────────────────────┐
                │                  NetSage_AI_Server                     │
                │        IP: 192.168.1.10/24 | GW: 192.168.1.1           │
                │     Services: DNS (netsage.ai) + HTTP Web Console      │
                └───────────────────────────┬────────────────────────────┘
                                            │ Fa0
                                            │
                ┌───────────────────────────┴────────────────────────────┐
                │                   Switch SW1 (2960)                    │
                │             Port Fa0/1 & Gi0/1 (VLAN 1)                │
                └───────────────────────────┬────────────────────────────┘
                                            │ Gi0/1
                                            │
                ┌───────────────────────────┴────────────────────────────┐
                │                    Netsage-Gateway                     │
                │                 Cisco 1941/2911 Router                 │
                │   Gig0/0: 192.168.1.1/24  |  Gig0/1: 192.168.2.1/24    │
                └───────────────────────────┬────────────────────────────┘
                                            │ Gi0/1
                                            │
                ┌───────────────────────────┴────────────────────────────┐
                │                   Switch SW2 (2960)                    │
                │            Port Gi0/1, Fa0/1, Fa0/2 (VLAN 1)           │
                └───────────────┬─────────────────────────┬──────────────┘
                                │ Fa0/1                   │ Fa0/2
                                │                         │
        ┌───────────────────────┴──────┐   ┌──────────────┴───────────────┐
        │           Admin-PC           │   │          Client-PC1          │
        │    IP: 192.168.2.10/24       │   │    IP: 192.168.2.20/24       │
        │    GW: 192.168.2.1           │   │    GW: 192.168.2.1           │
        │    DNS: 192.168.1.10         │   │    DNS: 192.168.1.10         │
        └──────────────────────────────┘   └──────────────────────────────┘
```

---

## 2. Quickstart & Local Development

### Option 1: Docker Compose (One-Command Full-Stack)

```bash
docker-compose up --build
```
- **Frontend Dashboard:** `http://localhost:3000` (or `http://localhost:5173`)
- **Backend API & Swagger Docs:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

### Option 2: Local Python & Node Setup

#### 1. Backend Setup (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Seed 35 Cisco network troubleshooting cases and baseline reviews
python scripts/seed_database.py

# Start development server
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup (React 19 / Vite)
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

#### 3. Standalone Python Rule Checker (No LLM Required)
```bash
# Run deterministic checks for CASE-001
python checker/rule_checker.py --case CASE-001

# Run checks across all 35 cases
python checker/rule_checker.py --all
```

---

## 3. VIP 2026 Deliverables Directory Tree

```
.
├── cases.csv                      # 35 structured troubleshooting cases
├── dataset/cases.csv              # Dataset archive
├── prompts/diagnose_prompt.md     # 12-field strict JSON prompt contract + 3 worked examples
├── checker/
│   ├── rule_checker.py            # Standalone Layer 1-7 deterministic Python rule engine
│   └── README.md                  # Rule engine guide & CLI usage
├── responsible_ai/
│   ├── review_log.csv             # Mandatory human review ledger
│   └── README.md                  # 5 documented human correction case studies
├── packet_tracer/
│   ├── README.md                  # Step-by-step human guide to build & save .pkt in Packet Tracer
│   ├── CASE_MAPPING.md            # 35-case topology & telemetry mapping matrix
│   ├── cases/                     # Individual Markdown specifications (CASE-001 to 035)
│   └── sample/CASE_001_InterVLAN_Routing/ # Primary sample case for demo and submission
│       ├── topology.md            # Dual-subnet NetSage-AI topology
│       ├── configuration.md       # Cisco IOS configuration commands
│       ├── broken_state.md        # Intentional fault injection
│       ├── fixed_state.md         # Staged remediation commands
│       ├── show_commands.md       # Required diagnostic commands
│       ├── show_outputs_before.txt# Broken state telemetry
│       ├── show_outputs_after.txt # Post-fix telemetry
│       └── expected_diagnosis.json# Contract-compliant AI output
├── docs/
│   ├── NetSageAI_Project_Report.md# Comprehensive 25-section project report
│   ├── DEMO_SCRIPT.md             # 5-10 minute demonstration script
│   └── REPOSITORY_AUDIT.md        # Codebase audit against VIP criteria
├── submission/
│   ├── SUBMISSION_CHECKLIST.md    # 3-file ZIP submission checklist
│   └── README.md                  # Packaging guide
├── backend/                       # FastAPI backend application
└── frontend/                      # React 19 + Tailwind CSS frontend
```

---

## 4. Final Submission Package (Maximum 3 Files Constraint)

Per official Cisco-AICTE VIP 2026 instructions, the final submission ZIP must contain **at most 3 files**:

```
NetSageAI_Submission.zip
│
├── NetSageAI_Project_Report.pdf                 # Exported from docs/NetSageAI_Project_Report.md
├── NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt# Created in Cisco Packet Tracer
└── NetSageAI_Source_Code.zip                    # Clean source code archive
```

---

## 5. Automated Testing & Verification

```bash
# Run backend test suite (126 unit & integration tests)
cd backend
pytest -v

# Run complete 17-point quality gate verification
python scripts/verify_system.py

# Build frontend production bundle
cd ../frontend
npm run build
```

---

## 6. License
NetSage-AI is licensed under the MIT License.
