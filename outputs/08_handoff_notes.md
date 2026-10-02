# Vireo Audio Support Intelligence — Operational Handoff Notes

**Recipient:** Priya Raman (Founder/CEO) & Neha (Support Operations Lead)  
**Date:** July 2026  
**System Version:** Task 1 V3 Production Release (Deterministic Engine)  

---

## 1. System Overview

This operational suite provides automated, zero-external-cost support intelligence for Vireo Audio. It replaces manual spreadsheet audits with two automated operational deliverables:
1. **Weekly Customer Complaint Digest:** A structured operational breakdown answering what customers complained about, WoW shifts, product defect concentrations, SLA compliance penalties, and direct financial costs.
2. **Weekly Agent Leaderboard:** A fair, tiered operational throughput tracking tool that enforces Support Policy §1 & §6 team boundaries (frontline volume ranking vs. multi-touch Tier 2 warranty investigations).

---

## 2. Quickstart & Execution Runbook

The tool requires only a standard Python environment (Python 3.10+) with zero external API credentials or paid infrastructure.

### Installation
```bash
pip install -r requirements.txt
```

### 1. Generate Weekly Complaint Digest
Generates both structured JSON telemetry and formatted Markdown reports for any target calendar week:
```bash
# Default reference week (2026-W26)
python scripts/04_generate_digest.py

# Custom week
python scripts/04_generate_digest.py --week 2026-W25
```
**Key Outputs:**
- `outputs/weekly_digest.md`: Human-readable digest formatted with 7 mandatory sections and `[FACT]` / `[HYPOTHESIS]` tags.
- `outputs/weekly_digest.json`: Full nested operational schema for downstream ingestion.
- `outputs/weekly_digest.csv`: Historical weekly telemetry spanning all 73 weeks for trend analysis.

### 2. Generate Weekly Agent Leaderboard
Computes tiered agent throughput for any target calendar week:
```bash
# Default reference week (2026-W26)
python scripts/05_agent_leaderboard.py

# Custom week
python scripts/05_agent_leaderboard.py --week 2026-W26
```
**Key Outputs:**
- `outputs/agent_leaderboard.md`: Frontline Tier 1 ranked leaderboard, separate Tier 2 Warranty / Escalations status roster (non-ranked), operational team roster, and management guardrails.
- `outputs/agent_leaderboard.csv`: Snapshot table for the reference week.
- `outputs/agent_weekly_metrics.csv`: Longitudinal throughput across all 73 weeks.

### 3. Run Quality & Classification Evaluation
Audits deterministic classification rules against the $N=120$ gold-standard human-audited benchmark and validates 8 deterministic policy assertions:
```bash
python scripts/05_evaluate.py
```
**Key Outputs:**
- `outputs/evaluation_report.md`: Benchmark accuracy scores, confusion matrices, and audit logs.
- `outputs/evaluation_results.json`: Machine-readable evaluation metrics.

### 4. Run Test Suite
Validates the entire analytical foundation and policy rules across 47 automated tests:
```bash
python -m pytest tests/ -q
```

---

## 3. Policy & Governance Rules

### Support Policy §1 & §6: Tier 1 vs Tier 2 Fair Ranking
- **Frontline (Tier 1):** Ranked by tickets closed per week. Owns first contact, rapid troubleshooting, and initial intake.
- **Warranty Desk & Tier 2 Escalations:** **NEVER** ranked on tickets closed per week. As documented by Support Ops, warranty investigations involve multi-day hardware triage, physical RMA returns, and vendor escalation. They are reported on a separate non-ranked roster tracking active investigations, average SLA adherence, and customer satisfaction.
- **Operational Specialists (Billing, Logistics, Returns Desk):** Reported separately with contextual volume and resolution rates appropriate for transactional operations.

### Repeat Contact Measurement
- **Policy Method A (Customer + SKU within 30 days):** 1,412 tickets (11.89% baseline, ₹367,030 handling cost). Recommended operational KPI for CRM deduplication.
- **Policy Method B (Customer Re-contact within 30 days):** 3,270 tickets (27.54% baseline, ₹878,120 handling cost). Broader customer retention indicator.
- **Text-Based Repeat Signal:** 1,457 tickets (12.27% baseline). Captures explicit re-contact phrasing in message content.
- **Customer Protest Subset:** 115 tickets (0.97% baseline). High-severity churn risks with severe escalation language.

---

## 4. Maintenance & Support

- **Runtime Cost:** ₹0.00 / month (no LLM tokens required).
- **Extensibility:** To enable experimental LLM classification or narrative synthesis, scripts support `--provider openai` / `--provider anthropic` when corresponding environment variables are configured.
