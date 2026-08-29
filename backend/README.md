# NetSage AI — Backend

AI-assisted Cisco network troubleshooting backend. Combines deterministic rule-based analysis with LLM diagnosis. **Human review is always required** before any diagnosis becomes final.

---

## Quick Start (Local)

```bash
# 1. Clone and enter backend
cd backend

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/Mac

# 5. (Optional) Edit .env — default AI_PROVIDER=mock works without any API key

# 6. Seed the database (35 realistic Cisco cases)
python scripts/seed_database.py

# 7. Start the server
uvicorn app.main:app --reload

# 8. Open docs
start http://localhost:8000/docs
```

---

## API Overview

All endpoints are under `/api/v1/`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/cases` | Create a case |
| `GET` | `/api/v1/cases` | List cases (paginated, filtered) |
| `GET` | `/api/v1/cases/{id}` | Get a case |
| `POST` | `/api/v1/cases/{id}/diagnose` | Run AI + rule diagnosis |
| `GET` | `/api/v1/cases/{id}/diagnoses` | List all diagnoses |
| `POST` | `/api/v1/cases/{id}/review` | Submit human review |
| `POST` | `/api/v1/cases/{id}/fix` | Record human-applied fix |
| `POST` | `/api/v1/cases/{id}/verify` | Record verification result |
| `GET` | `/api/v1/dashboard/summary` | Dashboard metrics |
| `GET` | `/api/v1/responsible-ai/summary` | Responsible AI metrics |
| `POST` | `/api/v1/evaluation/run` | Run internal evaluation |

**Interactive docs**: `http://localhost:8000/docs`

---

## Full Workflow Example

```bash
BASE=http://localhost:8000/api/v1

# 1. Diagnose a seeded case
curl -X POST $BASE/cases/CASE-001/diagnose | jq .

# 2. Accept the diagnosis (human review)
DIAG_ID=$(curl -s -X POST $BASE/cases/CASE-001/diagnose | jq .ai_diagnosis.id)
curl -X POST $BASE/cases/CASE-001/review \
  -H "Content-Type: application/json" \
  -d "{\"diagnosis_id\": $DIAG_ID, \"decision\": \"ACCEPTED\", \"reviewer\": \"engineer-1\"}"

# 3. Record fix (NOT auto-executed)
REVIEW_ID=$(curl -s $BASE/cases/CASE-001/reviews | jq '.[0].id')
curl -X POST $BASE/cases/CASE-001/fix \
  -H "Content-Type: application/json" \
  -d "{\"review_id\": $REVIEW_ID, \"commands\": [\"ip route 192.168.30.0 255.255.255.0 10.0.0.2\"], \"description\": \"Added missing static route\", \"performed_by\": \"engineer-1\"}"

# 4. Verify fix worked
curl -X POST $BASE/cases/CASE-001/verify \
  -H "Content-Type: application/json" \
  -d "{\"review_id\": $REVIEW_ID, \"verification_status\": \"SUCCESS\", \"verification_method\": \"PING\", \"verification_evidence\": \"Reply from 192.168.30.10\", \"verified_by\": \"engineer-1\"}"

# 5. Check responsible AI metrics
curl $BASE/responsible-ai/summary | jq .
```

---

## AI Providers

Set `AI_PROVIDER` in `.env`:

| Value | Description |
|-------|-------------|
| `mock` | **Default** — deterministic responses, no API key needed |
| `openai` | OpenAI GPT-4o — set `AI_API_KEY` |
| `gemini` | Google Gemini — set `AI_API_KEY` |
| `anthropic` | Anthropic Claude — set `AI_API_KEY` |

---

## Run Tests

```bash
pytest
# or with coverage
pytest --cov=app --cov-report=term-missing
```

---

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── core/                # Config, DB, logging, security, exceptions
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── parsers/             # Cisco show-command parsers
│   ├── rules/               # Deterministic rule engine (11 rules)
│   ├── ai/                  # AI provider abstraction (mock/OpenAI/Gemini/Anthropic)
│   ├── services/            # Business logic services
│   └── api/routes/          # FastAPI route handlers
├── data/
│   └── seed_cases.json      # 35 realistic Cisco troubleshooting cases
├── scripts/
│   ├── seed_database.py     # Seed DB with 35 cases
│   └── import_cases.py      # Import from CSV
├── prompts/                 # AI system prompts
└── tests/                   # Test suite (50+ tests)
```

---

## Safety Principles

- **Never executes Cisco commands** — commands are strings stored as data only
- **Human review always required** — `requires_human_review: true` is enforced at the API layer
- **AI is an assistant** — cannot autonomously modify networks
- **Evidence grounding** — AI citations cross-checked against supplied show outputs
- **Audit trail** — every significant event is logged to the `audit_logs` table

---

## Importing Custom Cases

```bash
# From CSV (see data/cases.csv for format)
python scripts/import_cases.py --file data/my_cases.csv

# Dry run (validate only)
python scripts/import_cases.py --file data/my_cases.csv --dry-run
```

CSV columns: `case_id, category, title, symptom, topology, show_outputs (JSON), expected_fault, expected_osi_layer, concept, severity, expected_fix (JSON), next_command, tags (JSON)`
