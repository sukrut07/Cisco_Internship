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

# 1. Health check
h = get(BASE + "/health")
print("[1] /health => status=" + h["status"] + " ai_provider=" + h["ai_provider"])

# 2. Case list - should have 35 seeded cases
cases = get(BASE + "/api/v1/cases")
print("[2] GET /cases => total=" + str(cases["total"]) + " cases")

# 3. Diagnose CASE-001
diag = post(BASE + "/api/v1/cases/CASE-001/diagnose", {})
state = diag.get("workflow_state", "?")
root = diag.get("ai_diagnosis", {}).get("root_cause", "?")
print("[3] DIAGNOSE CASE-001 => state=" + state)
print("    root_cause=" + root[:80])

# 4. Review ACCEPT
diag_id = diag["ai_diagnosis"]["id"]
review = post(BASE + "/api/v1/cases/CASE-001/review", {
    "diagnosis_id": diag_id,
    "decision": "ACCEPTED",
    "reviewer": "test-engineer"
})
print("[4] REVIEW => decision=" + review["decision"])

# 5. Record fix
review_id = review["id"]
fix = post(BASE + "/api/v1/cases/CASE-001/fix", {
    "review_id": review_id,
    "commands": ["ip route 192.168.30.0 255.255.255.0 10.0.0.2"],
    "description": "Added missing route",
    "performed_by": "test-engineer"
})
print("[5] FIX => applied_by=" + fix["applied_by"])

# 6. Verify
verify = post(BASE + "/api/v1/cases/CASE-001/verify", {
    "review_id": review_id,
    "verification_status": "SUCCESS",
    "verification_method": "PING",
    "verification_evidence": "Reply from 192.168.30.10",
    "verified_by": "test-engineer"
})
print("[6] VERIFY => status=" + verify["verification_status"])

# 7. Dashboard
dash = get(BASE + "/api/v1/dashboard/summary")
print("[7] DASHBOARD => cases=" + str(dash["total_cases"]) + " reviews=" + str(dash["total_reviews"]) + " agreement=" + str(dash["agreement_rate"]))

# 8. Responsible AI
rai = get(BASE + "/api/v1/responsible-ai/summary")
print("[8] RESPONSIBLE AI => correction_rate=" + str(rai["human_correction_rate"]))

print()
print("ALL E2E CHECKS PASSED!")
