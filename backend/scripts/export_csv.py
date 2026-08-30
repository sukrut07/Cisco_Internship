#!/usr/bin/env python3
"""Export seed_cases.json to cases.csv and dataset/cases.csv."""
import json
import csv
from pathlib import Path

seed_file = Path("backend/data/seed_cases.json")
with open(seed_file, encoding="utf-8") as f:
    cases = json.load(f)

dataset_dir = Path("dataset")
dataset_dir.mkdir(parents=True, exist_ok=True)

csv_paths = [Path("cases.csv"), dataset_dir / "cases.csv"]

fieldnames = [
    "case_id",
    "title",
    "category",
    "symptom",
    "topology_note",
    "show_outputs",
    "expected_fault",
    "osi_layer",
    "concept",
    "severity",
    "next_command",
    "expected_fix",
    "verification",
    "pkt_file"
]

rows = []
for c in cases:
    cid = c["case_id"]
    pkt = "NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt" if cid == "CASE-001" else "Lab_Scenario_Verified"
    
    show_snippets = []
    for cmd, out in c.get("show_outputs", {}).items():
        clean_out = " ".join(out.split())
        show_snippets.append(f"[{cmd}]: {clean_out}")
    show_text = " | ".join(show_snippets)
    fix_text = " -> ".join(c.get("expected_fix", []))
    
    rows.append({
        "case_id": cid,
        "title": c.get("title", ""),
        "category": c.get("category", ""),
        "symptom": c.get("symptom", ""),
        "topology_note": c.get("topology", ""),
        "show_outputs": show_text,
        "expected_fault": c.get("expected_fault", ""),
        "osi_layer": c.get("expected_osi_layer", ""),
        "concept": c.get("concept", ""),
        "severity": c.get("severity", ""),
        "next_command": c.get("next_command", ""),
        "expected_fix": fix_text,
        "verification": "Post-fix show commands and ICMP echo verification",
        "pkt_file": pkt
    })

for p in csv_paths:
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

print(f"Exported {len(rows)} cases to cases.csv and dataset/cases.csv")
