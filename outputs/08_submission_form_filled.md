# Vireo Audio Support Intelligence — Submission Form

### Candidate Information

- **Candidate Name:** KURUVA SURENDRA KUMAR
- **Candidate Email:** surendrakuruva571@gmail.com
- **Date of Submission:** 2 October 2026
- **Position Applied For:** Forward Deployed Engineer (FDE)

---

### Deliverable URLs
- **Public GitHub Repository URL:** https://github.com/Surendra571/vireo-support-intelligence
- **3-Minute Screen Recording URL (Google Drive):** 

---

### Part 1: Working AI-Assisted Tool

- **Repository Structure & Purpose:**
  A lightweight, reproducible Python support intelligence system tailored directly to Priya Raman's request (*"weekly digest of customer complaints + leaderboard of agents by tickets closed per week"* and *"Keep it simple, I don't need a platform"*).
- **Core Components:**
  1. **Data Cleaning & Deduplication (`scripts/01_profile_data.py`):** Resolves 3,125 duplicate tickets from legacy Freshdesk migration and applies +5h30m UTC offset correction to legacy resolution timestamps.
  2. **Deterministic & AI Classification (`scripts/04_classify_tickets.py`):** Classifies 11,875 tickets into 16 primary issues, 4 customer intents, and extracts text-based repeat signals without altering ground-truth records.
  3. **Weekly Customer Complaint Digest (`scripts/04_generate_digest.py`):** Outputs weekly complaint aggregations, Top 5 primary issue themes, week-over-week deltas, hardware defect concentrations, and policy-mandated variable cost drivers.
  4. **Weekly Agent Volume Leaderboard (`scripts/05_agent_leaderboard.py`):** Tracks frontline Tier 1 closure volumes across dynamic roster assignment dates for shift load balancing, while isolating Tier 2 (Warranty & Escalations) specialists into an unranked activity table.

---

### Part 2: Business Goal (Number + Money)

- **Validated Baseline (18 Months):**
  - Total Clean Tickets: **11,875**
  - Method A Repeat Contacts (Strict Issue Proxy): **1,412 tickets (11.89%)** | **₹367,030 handling cost** (₹61,171.67/quarter)
  - Method B Repeat Contacts (Product Proxy): **3,270 tickets (27.54%)** | **₹878,120 handling cost** (₹146,353.33/quarter)
- **Validated Candidate Goal Scenarios:**
  - **Option 1 (Conservative — Method A 10% Reduction):** Reduce Method A repeat contacts from 1,412 tickets (11.89%) to 1,271 tickets (10.70%) within 6 months post-deployment, equivalent to approximately **141 fewer repeat tickets** and **₹6,117 in potential avoided handling cost per quarter (₹24,469 annualized)**, subject to operational validation.
  - **Option 2 (Method A 20% Reduction / 12-Month Validation Target):** Reduce Method A repeat contacts from 1,412 tickets (11.89%) to 1,130 tickets (9.51%) within 12 months post-deployment, equivalent to approximately **282 fewer repeat tickets** and **₹12,234 in potential avoided handling cost per quarter (₹48,937 annualized)**, subject to operational validation.
  - **Option 3 (Pragmatic Operational Target — Method B 20% Reduction):** Reduce Method B product-level repeat contacts from 3,270 tickets (27.54%) to 2,616 tickets (22.03%) within 12 months post-deployment, equivalent to approximately **654 fewer re-contacts on the same device** and **₹29,271 in potential avoided handling cost per quarter (₹117,083 annualized)**, subject to operational validation.
- **Accounting Characterization:**
  All figures represent modeled potential avoided handling cost (capacity reclaim for frontline agents), not realized cash savings on payroll.

---

### Part 3: Validation Methodology

- **Empirical Evaluation Framework:**
  - Automated test suite covering 47 unit and integration tests across data ingestion, business calculations, classification taxonomy, digest structures, and agent roster logic (`python -m pytest tests/` -> 47 passed).
  - Validation protocol for repeat contact reduction: 2 quarters (6 months) for interim review; 4 quarters (12 months) for formal evaluation.
  - Primary metrics: Weekly Method A and Method B repeat-contact rates.
  - Secondary guardrails: Mean days to re-contact, CSAT response average, first-response SLA breach rate by channel, and internal transfer frequency.
  - Audit protocol: Manual review of flagged repeat signals and closed ticket notes to inspect resolution quality and diagnostic completeness. *Sample size and acceptable error threshold to be finalized during pilot design.*

---

### Part 4: One-Page Memo Highlights (Priya Raman)

- Located at: [`outputs/07_business_memo.md`](file:///d:/FDE_ASSIGNMENTS/vireo-support-intelligence/outputs/07_business_memo.md)
- Key Takeaways:
  1. Delivered simple, non-platform weekly digest and volume leaderboard with 0 external LLM API calls.
  2. Documented 18-month operational baseline: 11,875 tickets, 1,051 SLA breaches (₹367,850 store credit liability), 1,169 transfers (₹356,545 benchmark friction), and ₹3.87M in flagship defect cash outflows (Pulse 2 + Nexa 2).
  3. Formulated neutral repeat-contact reduction goal scenarios with explicit capacity vs cash accounting separation.
  4. Outlined operational next steps: deploy weekly digest in operational meetings, audit closing notes on high-repeat SKUs, and share upstream defect telemetry with Hardware Engineering and Logistics.

---

### Part 5: AI Usage & Cost Disclosure

- **Development Phase:** Generative AI was used for prompt iteration, code authoring, and documentation refinement. Exact development-time AI cost is not recorded in the repository.
- **Production Pipeline Execution:**
  - **External LLM Calls Made:** **0**
  - **Production Model Token Cost:** **$0.00 / ₹0.00**
  - **API Rate Limit Failures / Downtime Exposure:** **0**
  - Production classification and narrative compilation ran 100% deterministically offline using local rule-based taxonomy engines.

---

### Part 6: Known Limitations & Data Quality Notes

- **No `issue_id` Key:** The database schema lacks an issue tracking ID. Method A (same customer + SKU + category $\le$ 30d) and Method B (same customer + SKU $\le$ 30d) are analytical proxies, not ground-truth FCR measurements.
- **Sparse Message Data:** Approximately 3.7% of tickets lack explicit order IDs, and 23% of agent closing notes contain minimal placeholder text.
- **Tier 2 Incomparability:** Warranty and escalations require multi-day physical bench diagnosis and must never be evaluated against frontline volume metrics.
- **Accounting Boundary:** Frontline handling costs, SLA penalty store credits, internal transfer friction, and refund/replacement cash outflows are distinct accounting dimensions and are reported separately.
