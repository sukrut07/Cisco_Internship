# Submission Packaging Guide — Cisco-AICTE VIP 2026

This guide explains how to package the final submission archive for **NetSage AI**.

---

## 1. The 3-File ZIP Structure

Per the evaluation committee's instructions, create a single ZIP file containing **at most 3 files**:

```
NetSageAI_Submission.zip
│
├── NetSageAI_Project_Report.pdf
├── NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt
└── NetSageAI_Source_Code.zip
```

---

## 2. File Preparation Steps

### File 1: `NetSageAI_Project_Report.pdf`
1. Open [`docs/NetSageAI_Project_Report.md`](../docs/NetSageAI_Project_Report.md).
2. Export/print to PDF using your Markdown editor, VS Code extension ("Markdown PDF"), or Pandoc:
   ```bash
   # Or using pandoc / Chrome print
   pandoc docs/NetSageAI_Project_Report.md -o NetSageAI_Project_Report.pdf
   ```
3. Verify that all 25 sections and diagrams render cleanly.

### File 2: `NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt`
1. Follow the step-by-step instructions in [`packet_tracer/README.md`](../packet_tracer/README.md).
2. Build the topology in Cisco Packet Tracer and apply the configuration from [`packet_tracer/sample/CASE_001_InterVLAN_Routing/configuration.md`](../packet_tracer/sample/CASE_001_InterVLAN_Routing/configuration.md).
3. Save the broken baseline file as `NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt`.
4. Copy it into your submission directory.

### File 3: `NetSageAI_Source_Code.zip`
1. Create a clean archive of the project repository (excluding `.venv`, `node_modules`, `.git`, `__pycache__`):
   ```bash
   zip -r NetSageAI_Source_Code.zip . -x "*.venv*" "*node_modules*" "*.git*" "*__pycache__*" "*.DS_Store*" "*.pytest_cache*"
   ```

---

## 3. Creating the Final ZIP

```bash
zip -r NetSageAI_Submission.zip NetSageAI_Project_Report.pdf NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt NetSageAI_Source_Code.zip
```

Ensure your summary document is submitted separately via the designated Google Form upload field.
