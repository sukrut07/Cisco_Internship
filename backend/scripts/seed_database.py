#!/usr/bin/env python3
"""
NetSage AI — Database Seed Script.

Seeds the database with 35 realistic Cisco network troubleshooting cases.
Run from: backend/
  python scripts/seed_database.py
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import Base, engine, get_db_context
from app.core.logging_config import configure_logging
from app.models import _import_all_models  # noqa: ensures all models registered
from app.models.case import Case

configure_logging("INFO")
logger = logging.getLogger(__name__)

SEED_FILE = Path(__file__).parent.parent / "data" / "seed_cases.json"


def seed_database() -> None:
    """Seed the database with cases from seed_cases.json."""
    # Ensure tables exist
    _import_all_models()
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified.")

    if not SEED_FILE.exists():
        logger.error("Seed file not found: %s", SEED_FILE)
        sys.exit(1)

    with open(SEED_FILE, encoding="utf-8") as f:
        cases_data = json.load(f)

    logger.info("Loaded %d cases from seed file.", len(cases_data))

    created = 0
    skipped = 0

    with get_db_context() as db:
        for raw in cases_data:
            case_id = raw.get("case_id", "").upper()

            if not case_id:
                logger.warning("Skipping case with missing case_id: %s", raw.get("title"))
                skipped += 1
                continue

            # Check for existing case
            existing = db.query(Case).filter(Case.case_id == case_id).first()
            if existing:
                logger.debug("Case %s already exists — skipping.", case_id)
                skipped += 1
                continue

            case = Case(
                case_id=case_id,
                category=raw.get("category", "GENERAL").upper(),
                title=raw.get("title", ""),
                symptom=raw.get("symptom", ""),
                topology=raw.get("topology", ""),
                expected_fault=raw.get("expected_fault"),
                expected_osi_layer=raw.get("expected_osi_layer"),
                concept=raw.get("concept"),
                severity=raw.get("severity", "MEDIUM").upper(),
                next_command=raw.get("next_command"),
                workflow_state="CREATED",
            )
            case.show_outputs_dict = raw.get("show_outputs", {})
            case.expected_fix_list = raw.get("expected_fix", [])
            case.tags_list = raw.get("tags", [])

            db.add(case)
            created += 1
            logger.info("Created: %s — %s", case_id, raw.get("title", ""))

    logger.info("Seed complete: %d created, %d skipped.", created, skipped)
    print(f"\nSeed complete: {created} cases created, {skipped} skipped.")
    print("   Run: uvicorn app.main:app --reload")
    print("   Then open: http://localhost:8000/docs")


if __name__ == "__main__":
    seed_database()
