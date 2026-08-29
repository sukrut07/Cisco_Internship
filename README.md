# NetSage AI

> AI-assisted Cisco network troubleshooting system for Packet Tracer / lab environments.

---

## Project Structure

```
cisco/
├── backend/          Python (FastAPI) — AI diagnosis + rule engine + REST API
│   ├── app/          Application code
│   ├── data/         35 seed cases (JSON)
│   ├── tests/        94 automated tests
│   ├── scripts/      Seed, import, and smoke-test scripts
│   ├── prompts/      AI system prompts
│   ├── Dockerfile
│   └── README.md     → Backend-specific docs
│
└── frontend/         React / Next.js (team-managed, separate branch)
```

---

## What It Does

NetSage AI accepts:
- Network symptom description
- Topology diagram (text)
- Cisco `show` command outputs
- (Optional) structured device configuration

And produces:
- Likely root cause + confidence level
- OSI layer classification
- Evidence citations grounded in supplied `show` outputs
- Next diagnostic command to run
- Recommended human-reviewed fix steps

**Safety constraint**: The AI never executes commands. Every diagnosis requires human review before any action is taken.

---

## Workflow

```
         ┌─────────────┐
         │ Submit Case  │
         └──────┬──────┘
                │
         ┌──────▼──────────────┐
         │  Rule Engine        │  ← 11 deterministic rules
         │  (Layer 1-7 checks) │
         └──────┬──────────────┘
                │
         ┌──────▼──────────────┐
         │  AI Diagnosis       │  ← mock / OpenAI / Gemini / Anthropic
         │  + Evidence Grounding│
         └──────┬──────────────┘
                │
         ┌──────▼────────────────────┐
         │  AWAITING HUMAN REVIEW    │  ← mandatory stop
         └──────┬────────────────────┘
                │  ACCEPTED / EDITED / REJECTED
         ┌──────▼──────────────┐
         │  Fix Recorded       │  ← human-entered, never auto-applied
         └──────┬──────────────┘
                │
         ┌──────▼──────────────┐
         │  Verification       │  ← ping / show command / manual
         └─────────────────────┘
```

---

## Quick Start — Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python scripts\seed_database.py        # loads 35 Cisco cases
uvicorn app.main:app --reload
# Docs: http://localhost:8000/docs
```

Full backend documentation → [backend/README.md](./backend/README.md)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI (Python 3.11+) |
| Database | SQLite (WAL mode) via SQLAlchemy 2.0 |
| AI Providers | OpenAI, Google Gemini, Anthropic Claude, Mock |
| Frontend | React / Next.js (team) |
| Tests | pytest (94 tests) |
| Containerisation | Docker + docker-compose |

---

## Team

- **Backend** — AI engine, rule engine, REST API
- **Frontend** — UI / dashboard (separate team)
