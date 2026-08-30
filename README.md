# NetSage AI

> **AI-Assisted Cisco / Packet Tracer Network Troubleshooting Platform with Deterministic Rule Checking and Mandatory Human-in-the-Loop Review.**

---

## Architecture Overview

NetSage AI bridges the gap between probabilistic generative AI and strict network engineering standards by combining:
1. **Deterministic Rule Engine (Layer 1–7):** 11 protocol checks (interface state, duplicate IP, subnet masks, default gateways, static/dynamic routing, VLAN trunking, ACL deny filters, NAT translations, DHCP snooping/pools, and DNS resolution).
2. **Multi-Provider AI Grounding Engine:** Supports Mock, OpenAI, Google Gemini, and Anthropic Claude with strict anti-hallucination citation parsing against Cisco `show` command outputs.
3. **Mandatory Human-in-the-Loop Review Gate:** AI provides diagnostic recommendations and stages CLI remediation commands; authorized human engineers must explicitly review (`ACCEPTED`, `EDITED`, or `REJECTED`) before fix staging or verification.
4. **Immutable Audit Trail:** Append-only cryptographic-style audit logging for compliance, review traceability, and prompt recalibration.
5. **Modern Glassmorphism Frontend:** High-performance React 19 + Vite dashboard featuring real-time diagnostic telemetry, live topology inspection, confidence gauges, and responsible AI discrepancy ledger.

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

---

## Quickstart Guide

### Option 1: Docker Compose (Production Deployment)

```bash
# Clone repository and launch containers
docker-compose up --build
```

- **Frontend Application:** `http://localhost:3000`
- **Backend API & Swagger Docs:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

---

### Option 2: Local Development Setup

#### 1. Backend Setup (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed database with 35 Cisco network troubleshooting cases and baseline reviews
python scripts/seed_database.py

# Start development server
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup (React / Vite)

```bash
# In a separate terminal, navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Live system health and configured AI provider |
| `GET` | `/ready` | Database connection and migration readiness |
| `GET` | `/api/v1/cases` | Paginated catalog of Cisco troubleshooting cases |
| `GET` | `/api/v1/cases/{case_id}` | Detailed case metadata and topology |
| `GET` | `/api/v1/cases/{case_id}/evidence` | Structured evidence extracted from `show` outputs |
| `POST` | `/api/v1/cases/{case_id}/diagnose` | Run AI grounded diagnosis & deterministic rule checks |
| `POST` | `/api/v1/cases/{case_id}/reviews` | Submit mandatory human engineer review decision |
| `POST` | `/api/v1/cases/{case_id}/fix` | Record staged human remediation CLI commands |
| `POST` | `/api/v1/cases/{case_id}/verification` | Record post-fix verification test results |
| `GET` | `/api/v1/cases/{case_id}/audit-trail` | Immutable chronological audit events for case |
| `GET` | `/api/v1/audit/logs` | Global paginated compliance audit ledger |
| `GET` | `/api/v1/dashboard/summary` | Live operational troubleshooting KPIs and stats |
| `GET` | `/api/v1/responsible-ai/summary` | Human correction metrics & AI agreement rates |
| `GET` | `/api/v1/responsible-ai/corrections` | Ledger of human engineer diagnostic overrides |
| `POST` | `/api/v1/evaluation/run` | Benchmark evaluation run against 35 seed cases |

---

## Safety & Responsible AI Guarantees

1. **Zero Autonomous CLI Execution:** NetSage AI strictly prevents direct execution of Cisco commands (`subprocess`, `os.system`, `netmiko`, `ssh`, or `telnet` are forbidden). All remediation CLI is staged for human engineer execution.
2. **Evidence Grounding:** AI diagnostic output is validated against supplied Cisco `show` command telemetry. Claims without exact telemetry citations are flagged as `UNGROUNDED` or `PARTIALLY_GROUNDED`.
3. **Discrepancy Ledger:** Human overrides (`EDITED` or `REJECTED`) are indexed to continuously evaluate model calibration and eliminate hallucinations.

---

## Automated Test Suite

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

## License

Proprietary — NetSage AI Cisco Troubleshooting Platform.
