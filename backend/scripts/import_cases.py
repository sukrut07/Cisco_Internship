#!/usr/bin/env python3
"""
NetSage AI — CSV Case Import Script.

Imports cases from data/cases.csv into the database.
Run from: backend/
  python scripts/import_cases.py [--file path/to/cases.csv]
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import Base, engine, get_db_context
from app.core.logging_config import configure_logging
from app.models import _import_all_models
from app.models.case import Case

configure_logging("INFO")
logger = logging.getLogger(__name__)

DEFAULT_CSV = Path(__file__).parent.parent / "data" / "cases.csv"

REQUIRED_COLUMNS = {"case_id", "category", "title", "symptom", "topology"}
OPTIONAL_JSON_COLUMNS = {"show_outputs", "expected_fix", "tags"}


def parse_row(row: dict[str, str], row_num: int) -> dict[str, Any] | None:
    """Validate and parse a single CSV row."""
    errors = []

    # Required fields
    for col in REQUIRED_COLUMNS:
        if not row.get(col, "").strip():
            errors.append(f"Missing required field: {col}")

    case_id = row.get("case_id", "").strip().upper()
    import re
    if case_id and not re.match(r"^[A-Z0-9\-_]{1,50}$", case_id):
        errors.append(f"Invalid case_id format: {case_id}")

    severity = row.get("severity", "MEDIUM").strip().upper()
    if severity not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        logger.warning("Row %d: Invalid severity '%s', defaulting to MEDIUM", row_num, severity)
        severity = "MEDIUM"

    if errors:
        logger.error("Row %d (%s): %s", row_num, case_id, "; ".join(errors))
        return None

    # Parse JSON fields
    show_outputs = {}
    expected_fix = []
    tags = []

    for field, default in [("show_outputs", "{}"), ("expected_fix", "[]"), ("tags", "[]")]:
        raw = row.get(field, "").strip()
        if raw:
            try:
                parsed = json.loads(raw)
                if field == "show_outputs":
                    show_outputs = parsed if isinstance(parsed, dict) else {}
                elif field == "expected_fix":
                    expected_fix = parsed if isinstance(parsed, list) else []
                elif field == "tags":
                    tags = parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                logger.warning("Row %d: Could not parse JSON for field '%s'", row_num, field)

    return {
        "case_id": case_id,
        "category": row.get("category", "GENERAL").strip().upper(),
        "title": row.get("title", "").strip(),
        "symptom": row.get("symptom", "").strip(),
        "topology": row.get("topology", "").strip(),
        "show_outputs": show_outputs,
        "expected_fault": row.get("expected_fault", "").strip() or None,
        "expected_osi_layer": row.get("expected_osi_layer", "").strip() or None,
        "concept": row.get("concept", "").strip() or None,
        "severity": severity,
        "expected_fix": expected_fix,
        "next_command": row.get("next_command", "").strip() or None,
        "tags": tags,
    }


def import_csv(csv_path: Path, dry_run: bool = False) -> None:
    """Import cases from a CSV file."""
    if not csv_path.exists():
        logger.error("CSV file not found: %s", csv_path)
        sys.exit(1)

    _import_all_models()
    Base.metadata.create_all(bind=engine)

    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    logger.info("Read %d rows from %s", len(rows), csv_path)

    parsed_cases = []
    for i, row in enumerate(rows, start=2):
        parsed = parse_row(row, i)
        if parsed:
            parsed_cases.append(parsed)

    logger.info("%d/%d rows are valid.", len(parsed_cases), len(rows))

    if dry_run:
        print(f"Dry run: {len(parsed_cases)} valid cases would be imported.")
        return

    created = skipped = errors = 0

    with get_db_context() as db:
        for data in parsed_cases:
            existing = db.query(Case).filter(Case.case_id == data["case_id"]).first()
            if existing:
                skipped += 1
                continue

            try:
                case = Case(
                    case_id=data["case_id"],
                    category=data["category"],
                    title=data["title"],
                    symptom=data["symptom"],
                    topology=data["topology"],
                    expected_fault=data.get("expected_fault"),
                    expected_osi_layer=data.get("expected_osi_layer"),
                    concept=data.get("concept"),
                    severity=data["severity"],
                    next_command=data.get("next_command"),
                    workflow_state="CREATED",
                )
                case.show_outputs_dict = data["show_outputs"]
                case.expected_fix_list = data["expected_fix"]
                case.tags_list = data["tags"]
                db.add(case)
                created += 1
            except Exception as exc:
                logger.error("Failed to create case %s: %s", data["case_id"], exc)
                errors += 1

    print(f"\n✅ Import complete: {created} created, {skipped} skipped, {errors} errors.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import cases from CSV")
    parser.add_argument("--file", default=str(DEFAULT_CSV), help="Path to CSV file")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, don't import")
    args = parser.parse_args()

    import_csv(Path(args.file), dry_run=args.dry_run)
