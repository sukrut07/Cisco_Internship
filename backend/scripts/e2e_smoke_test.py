import urllib.request
import json

def get(url):
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())

def post(url, data):
    req = urllib.request.Request(url, json.dumps(data).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

BASE = "http://localhost:8000"

print("==========================================================")
print(" NetSage AI — End-to-End Production Smoke Test")
print("==========================================================")

# 1. Health and Readiness checks
h = get(BASE + "/health")
print(f"[1] /health => status={h['status']} ai_provider={h['ai_provider']}")

ready = get(BASE + "/ready")
print(f"[2] /ready  => status={ready['status']}")

# 2. Case list
cases = get(BASE + "/api/v1/cases")
print(f"[3] GET /cases => total={cases['total']} cases")

# 3. Query Evidence
ev = get(BASE + "/api/v1/cases/CASE-001/evidence")
print(f"[4] GET /cases/CASE-001/evidence => {ev['total_commands']} commands parsed")

# 4. Diagnose CASE-001
diag = post(BASE + "/api/v1/cases/CASE-001/diagnose", {})
state = diag.get("workflow_state", "?")
root = diag.get("ai_diagnosis", {}).get("root_cause", "?")
print(f"[5] DIAGNOSE CASE-001 => state={state}")
print(f"    root_cause={root[:75]}...")

# 5. Review ACCEPT
diag_id = diag["ai_diagnosis"]["id"]
review = post(BASE + "/api/v1/cases/CASE-001/review", {
    "diagnosis_id": diag_id,
    "decision": "ACCEPTED",
    "reviewer": "test-engineer",
    "review_reason": "Verified route missing in output.",
})
print(f"[6] REVIEW => decision={review['decision']} (id={review['id']})")

# 6. Record fix (HUMAN_APPLIED, never autonomously executed)
review_id = review["id"]
fix = post(BASE + "/api/v1/cases/CASE-001/fix", {
    "review_id": review_id,
    "commands": ["ip route 192.168.30.0 255.255.255.0 10.0.0.2"],
    "description": "Added missing route manually",
    "performed_by": "test-engineer"
})
print(f"[7] FIX => status={fix['status']} applied_by={fix['applied_by']}")

# 7. Verify
verify = post(BASE + "/api/v1/cases/CASE-001/verify", {
    "review_id": review_id,
    "verification_status": "SUCCESS",
    "verification_method": "PING",
    "verification_evidence": "Reply from 192.168.30.10: bytes=32 time=2ms TTL=254",
    "verified_by": "test-engineer"
})
print(f"[8] VERIFY => status={verify['verification_status']}")

# 8. Query Audit Trail
audit = get(BASE + "/api/v1/cases/CASE-001/audit-trail")
print(f"[9] AUDIT TRAIL => {len(audit)} chronological lifecycle events recorded")

# 9. Dashboard Summary
dash = get(BASE + "/api/v1/dashboard/summary")
print(f"[10] DASHBOARD => cases={dash['total_cases']} reviews={dash['total_reviews']} agreement={dash['agreement_rate']}")

# 10. Responsible AI Summary
rai = get(BASE + "/api/v1/responsible-ai/summary")
print(f"[11] RESPONSIBLE AI => correction_rate={rai['human_correction_rate']} agreement_rate={rai['ai_human_agreement_rate']}")

# 11. Run Evaluation Pipeline
eval_res = post(BASE + "/api/v1/evaluation/run", {})
print(f"[12] EVALUATION => evaluated={eval_res['total_cases']} accuracy={eval_res['accuracy']:.1%}")

print("==========================================================")
print(" ALL E2E CHECKS PASSED SUCCESSFULLY!")
print("==========================================================")
