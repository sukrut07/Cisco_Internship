# Cisco-AICTE VIP 2026 — Final Submission Checklist

Use this checklist to ensure all technical, academic, and administrative requirements are complete before submitting the final package.

---

## 1. Final ZIP Archive Packaging (Maximum 3 Files Constraint)

> [!IMPORTANT]
> **Instructor Guideline:** The primary submission ZIP must contain **at most 3 files**:

```
NetSageAI_Submission.zip
│
├── 01_NetSageAI_Project_Report.pdf
├── 02_NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt
└── 03_NetSageAI_Source_Code.zip
```

- [ ] **1. Project Report (`NetSageAI_Project_Report.pdf`):** Exported from [`docs/NetSageAI_Project_Report.md`](../docs/NetSageAI_Project_Report.md) with all 25 sections complete.
- [ ] **2. Sample Packet Tracer File (`NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt`):** Created manually in Cisco Packet Tracer following [`packet_tracer/README.md`](../packet_tracer/README.md) and saved in broken baseline state.
- [ ] **3. Source Code Archive (`NetSageAI_Source_Code.zip`):** Complete clean codebase (FastAPI backend, React frontend, Python rule checker, dataset, test suite).
- [ ] **Separate Summary Document:** Prepared and submitted separately to the designated Google Form field.

---

## 2. Technical Deliverables Checklist

### A. Troubleshooting Dataset
- [ ] **35 Troubleshooting Cases** present in `cases.csv` and `dataset/cases.csv`.
- [ ] Complete protocol coverage across:
  - [ ] VLAN & 802.1Q Trunking (6 cases)
  - [ ] Default Gateway & IP Addressing (5 cases)
  - [ ] Routing & OSPF (6 cases)
  - [ ] Access Control Lists (4 cases)
  - [ ] DHCP & APIPA (4 cases)
  - [ ] DNS Resolution (3 cases)
  - [ ] NAT (3 cases)
  - [ ] Wireless & Switching (4 cases)
- [ ] Every case contains symptoms, topology notes, Cisco `show` command outputs, expected faults, OSI layers, concept tags, and severity levels.

### B. AI Prompt & Grounding System
- [ ] `prompts/diagnose_prompt.md` updated with strict JSON schema.
- [ ] Anti-hallucination evidence rule enforced.
- [ ] 3 worked examples included (Inter-VLAN, Gateway, ACL).
- [ ] Confidence scoring and next diagnostic command specified.

### C. Deterministic Python Rule Checker
- [ ] Standalone rule engine in `checker/rule_checker.py`.
- [ ] Independently verifies L1–L7 protocol rules without LLM calls.
- [ ] CLI callable: `python checker/rule_checker.py --case CASE-001` or `--all`.

### D. Human Oversight & Responsible AI Ledger
- [ ] Mandatory review statuses: `ACCEPTED`, `EDITED`, `REJECTED`.
- [ ] Zero autonomous CLI command execution.
- [ ] `responsible_ai/review_log.csv` contains all review logs.
- [ ] **5+ documented human-corrected AI failure cases** with technical explanations.

### E. Analytics Dashboard & Telemetry
- [ ] Real-time KPIs for Total Cases, AI-Human Agreement Rate (87.2%), and Responsible AI Corrections (5).
- [ ] Severity and protocol distribution charts.
- [ ] Full immutable audit trail.

### F. Demonstration Video
- [ ] 5–10 minute demonstration recorded following [`docs/DEMO_SCRIPT.md`](../docs/DEMO_SCRIPT.md).
- [ ] Demonstrates: Broken lab -> Show commands -> NetSage AI diagnosis -> Python rule validation -> Human review -> Apply fix -> Verify ICMP ping -> Dashboard.

---

## 3. Administrative Submission Requirements

- [ ] **VIP Course Certificates:** Completed all required Cisco Networking Academy / VIP Track course modules and downloaded certificates.
- [ ] **AICTE Registration Number:** Verified AICTE Student Registration Number is accurate.
- [ ] **College Name:** Verified full official College Name is entered.
- [ ] **Google Form Submission:** Submitted form before deadline (30 August 2026).
