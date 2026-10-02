# Step 6 — Agent Leaderboard Technical Validation Report
**Vireo Audio Support Intelligence Assessment**  
**Date:** October 2, 2026 | **Status:** Validated & Audited | **Version:** 1.0

---

## 1. Executive Summary & Objective

The objective of **Step 6** is to construct a deterministic, policy-compliant weekly agent attendance and closure leaderboard to fulfill the requirement requested by Priya Raman (Head of CX) while strictly adhering to the operational policy constraints highlighted by Neha Kulkarni (Support Operations Manager):
> *"weekly digest of customer complaints + leaderboard of agents by tickets closed per week"*  
> *"Please don't rank the warranty team on ticket counts — their cases take days."* (Neha Kulkarni, Support Ops)

### Key Architectural & Governance Decisions:
1. **Strict Tier Isolation:** Tier 1 agents (Frontline and operational process owners) are ranked on ticket closures per week. Tier 2 agents (Escalations & Warranty) are **never ranked against Tier 1**; their volume is presented in a separate descriptive section without ranking.
2. **Attendance Definition:** Attendance is defined strictly as completed tickets (status `resolved` or `closed`) per Support Policy v3.2 §10. Open and pending tickets are excluded.
3. **Resolving Agent Attribution:** Every ticket is credited strictly to the resolving agent (`agent_id`) who closed the case, regardless of initial team assignment or transfers.
4. **Zero Join Multiplication:** Agents roster (`agents.csv`) is matched by date validity intervals (`from_date` to `to_date`), ensuring zero record inflation.
5. **No Evaluative Claims:** Leaderboard explicitly measures **throughput volume**, not employee quality. No arbitrary composite performance score is generated.

---

## 2. Source Data & Methodology

### 2.1 Data Sources
- `data/tickets.csv`: 12,528 raw records (11,875 clean tickets post-deduplication).
- `data/agents.csv`: 44 agent assignment records across 7 functional teams.
- `outputs/classified_tickets.csv`: 11,875 pre-classified ticket records providing deterministic text-based repeat signal telemetry.
- `data/support-policy.pdf`: Support Operating Policy v3.2 (§3 SLAs, §6 Teams & Tiers, §7 Roster, §8 CSAT, §10 Reporting Definitions).

### 2.2 Deduplication Methodology
As established in Step 1, 653 duplicate ticket IDs (1,306 rows) exist between `helpdesk` and `legacy_fd` systems due to migration re-import. Deduplication prioritizes `helpdesk` over `legacy_fd`:
- Raw tickets: **12,528**
- Deduplicated corpus: **11,875**
- Legacy resolution timestamp correction: Legacy Freshdesk resolution timestamps reconstructed in UTC are converted to Indian Standard Time (IST, UTC+05:30) per Support Policy §9.

### 2.3 Ticket Completion Definition
Support Policy v3.2 §10 defines:
- **Completed Attendance:** Any ticket with status `resolved` or `closed`.
- **Exclusion:** Tickets with status `open` (376) and `pending` (233) are strictly omitted from attendance and closure rankings.
- Completed tickets: **11,266** (10,159 resolved + 1,107 closed).

### 2.4 Weekly Convention & Date Normalization
- **ISO Week Standard:** Week identifier uses ISO week formatting `%G-W%V` (Monday to Sunday) based on `resolved_at_dt`.
- **Reporting Week Range:** Matches Step 5 weekly digest convention.
- **Calendar Boundary Flags:** Weeks with fewer than 7 recorded operational days (such as `2025-W01` with 5 days, or tail week `2026-W28` with 3 days) are flagged with `complete_week = False`.
- Reference analysis week: **`2026-W26`** (2026-06-22 to 2026-06-28), which is a complete 7-day operating week.

### 2.5 Agent Roster Join Integrity
- Roster records in `agents.csv` represent assignment periods with `from_date` and `to_date`.
- Each ticket is mapped to the agent's applicable assignment row on the ticket resolution date:
  $$\text{from\_date} \le \text{resolved\_at\_dt} \le \text{to\_date}$$
- All 44 agents in `agents.csv` currently feature active open-ended assignments (`to_date = NaN`, treated as ongoing).
- **Join Multiplier Verification:**
  - Completed tickets before join: **11,266**
  - Completed tickets after join: **11,266**
  - Row inflation factor: **1.0000x (zero duplicate row generation)**.

---

## 3. Tier Handling & Classification Rules

Support Policy v3.2 §6 establishes clear operational boundaries between support tiers:

| Tier | Teams Included | Roster Count | Primary Workflow | Leaderboard Treatment |
| :---: | :--- | :---: | :--- | :--- |
| **Tier 1** | Chat Frontline, Email Frontline, Voice Frontline, Logistics, Billing, Returns Desk | 38 agents | First-contact resolution, delivery tracking, billing adjustments, refund processing | **Eligible for weekly volume ranking** (`rank_within_tier1` assigned) |
| **Tier 2** | Escalations & Warranty | 6 agents | Certified hardware diagnostics, warranty claims, multi-day bench investigations | **Descriptive volume only — NOT ranked** (`rank_within_tier1 = NaN`) |

### Why Tier 2 Is Excluded from Ranking:
Policy §6 explicitly states:
> *"Tier 2 work is certified: only Tier 2 agents may approve warranty replacements. Tier 2 cases are multi-touch by nature and are measured on resolution in days, not on tickets closed per week. Tier 2 agents are not to be compared with Tier 1 on volume metrics."*

Ranking Tier 2 against Tier 1 would create perverse incentives, punishing agents handling complex certified hardware investigations that require multi-day diagnostic bench tests.

---

## 4. Corpus Reconciliation Matrix

Before publishing, ticket closure attribution was reconciled against the complete 18-month ticket dataset:

| Category | Ticket Count | Share of Total (%) | Reconciliation Notes |
| :--- | :---: | :---: | :--- |
| **Total Raw Tickets** | 12,528 | — | Includes 653 re-imported duplicate pairs |
| **Deduplicated Ticket Corpus** | 11,875 | 100.00% | Unique `ticket_id` baseline |
| **Open / Pending Tickets (Excluded)** | 609 | 5.13% | 376 Open + 233 Pending (incomplete attendance) |
| **Total Completed Tickets (Resolved / Closed)** | **11,266** | **94.87%** | 10,159 Resolved + 1,107 Closed |
| ↳ *Completed Attributed to Valid Agent* | **11,266** | 100.00% | 100% matched to canonical roster |
| ↳ *Completed Missing Valid Agent Attribution* | **0** | 0.00% | Zero orphan or unassigned tickets |
| ↳ *Tier 1 Completed Tickets* | **10,547** | 93.62% | Across 38 Tier 1 agents |
| ↳ *Tier 2 Completed Tickets* | **719** | 6.38% | Across 6 Escalations & Warranty agents |
| ↳ *Other / Unclassified Team Completed Tickets* | **0** | 0.00% | 100% team taxonomy coverage |

$$\text{Tier 1 Completed (10,547)} + \text{Tier 2 Completed (719)} = \text{Total Completed (11,266)}$$

---

## 5. Metrics & Calculation Formulas

For each agent and week in `outputs/agent_leaderboard.csv`:

1. **Tickets Closed ($N_i$):**
   $$N_i = \sum \mathbf{1}_{\{\text{agent}=\text{agent}_i, \text{week}=\text{week}_k, \text{status}\in[\text{'resolved'}, \text{'closed'}]\}}$$
2. **Share of Tier 1 Closures (%):**
   $$\text{Share}_i = \frac{N_i}{\sum_{j \in \text{Tier 1}} N_j} \times 100$$
   *(Defined only for Tier 1 agents; left null for Tier 2).*
3. **Tier 1 Volume Rank:**
   $$\text{Rank}_i = 1 + \sum_{j \in \text{Tier 1}} \mathbf{1}_{\{N_j > N_i\}}$$
   *(Method `min` ranking; ties receive identical rank, deterministically sorted by `agent_id`).*
4. **Week-over-Week Absolute Change:**
   $$\Delta N_i = N_i(w) - N_i(w-1)$$
5. **Week-over-Week Percentage Change:**
   $$\%\Delta N_i = \begin{cases} \frac{N_i(w) - N_i(w-1)}{N_i(w-1)} \times 100 & \text{if } N_i(w-1) > 0 \\ \text{NaN} & \text{if } N_i(w-1) = 0 \text{ (safe handling)} \end{cases}$$
6. **First-Response SLA Breach Rate (%):**
   $$\text{SLA Breach Rate}_i = \frac{\text{SLA Breaches}_i}{N_i} \times 100$$
   *(Target: Chat 15m, Voice 120m, Social 240m, Email 480m per Policy §3).*
7. **Text-Based Repeat Signal Count:**
   Number of tickets closed by agent containing customer protest phrases indicating prior unaddressed contact (Step 4 classifier).

---

## 6. Latest Complete Week Output (`2026-W26`: June 22–28, 2026)

- **Total Active Agents in W26:** 44 agents (38 Tier 1, 6 Tier 2).
- **Total Tickets Closed in W26:** 192 tickets (181 Tier 1 + 11 Tier 2).

### Top 10 Tier 1 Agents (Ranked by Closure Volume)
| Rank | Agent ID | Agent Name | Team | Tickets Closed | Share (%) | WoW Change | SLA Breaches | Repeat Signals |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | `A3021` | Pooja Dhillon | Email Frontline | **11** | 6.08% | +6 (+120.0%) | 1 (9.1%) | 0 |
| **1** | `A3037` | Vivaan Sethi | Returns Desk | **11** | 6.08% | +4 (+57.1%) | 0 (0.0%) | 4 |
| **3** | `A3031` | Aishwarya Agarwal | Logistics | **10** | 5.52% | +3 (+42.9%) | 1 (10.0%) | 2 |
| **3** | `A3033` | Diya Singh | Billing | **10** | 5.52% | +1 (+11.1%) | 0 (0.0%) | 0 |
| **5** | `A3010` | Om Varghese | Chat Frontline | **9** | 4.97% | +8 (+800.0%) | 0 (0.0%) | 0 |
| **5** | `A3028` | Tarun Pereira | Logistics | **9** | 4.97% | +5 (+125.0%) | 1 (11.1%) | 2 |
| **7** | `A3016` | Ayaan Pawar | Email Frontline | **8** | 4.42% | +3 (+60.0%) | 1 (12.5%) | 2 |
| **7** | `A3019` | Kavya D'Souza | Email Frontline | **8** | 4.42% | +3 (+60.0%) | 0 (0.0%) | 0 |
| **7** | `A3029` | Geeta Rathore | Logistics | **8** | 4.42% | +1 (+14.3%) | 0 (0.0%) | 1 |
| **10** | `A3027` | Rajat Saxena | Logistics | **7** | 3.87% | -3 (-30.0%) | 1 (14.3%) | 0 |

*(Note: Rank reflects ticket closure volume only; it is not an overall performance score).*

### Tier 2 Escalations & Warranty Activity (Descriptive Volume Only — Not Ranked)
| Agent ID | Agent Name | Team | Tickets Closed | WoW Change | SLA Breaches | Repeat Signals |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| `A3040` | Sai Sharma | Escalations & Warranty | **3** | +2 (+200.0%) | 2 (66.7%) | 1 |
| `A3041` | Deepak Mathew | Escalations & Warranty | **2** | 0 (0.0%) | 0 (0.0%) | 0 |
| `A3042` | Aishwarya Kaur | Escalations & Warranty | **2** | +1 (+100.0%) | 0 (0.0%) | 0 |
| `A3044` | Meera Joshi | Escalations & Warranty | **2** | 0 (0.0%) | 0 (0.0%) | 0 |
| `A3039` | Vivaan Kulkarni | Escalations & Warranty | **1** | 0 (0.0%) | 0 (0.0%) | 0 |
| `A3043` | Rahul Gupta | Escalations & Warranty | **1** | -1 (-50.0%) | 1 (100.0%) | 0 |

---

## 7. Test Results & Validation Suite

Validation is codified in [`tests/test_agent_leaderboard.py`](file:///d:/FDE_ASSIGNMENTS/vireo-support-intelligence/tests/test_agent_leaderboard.py), covering all 16 evaluation areas:
1. `test_weekly_grouping_convention`: Verified ISO week (%G-W%V) and Monday-Sunday date bounds.
2. `test_only_completed_tickets_counted`: Verified only `resolved` and `closed` tickets are included; `open` and `pending` are excluded.
3. `test_resolving_agent_attribution`: Verified closure credit strictly belongs to the closing `agent_id`.
4. `test_deduplication_integrity`: Verified 653 re-imported tickets do not inflate closure counts.
5. `test_agent_join_no_multiplication`: Verified ticket counts before and after roster merge are exactly 11,266.
6. `test_tier_1_agents_ranked`: Verified Tier 1 agents receive integer ranks.
7. `test_tier_2_agents_no_tier_1_rank`: Verified Tier 2 agents have `rank_within_tier1 = NaN`.
8. `test_tier_2_tickets_descriptively_visible`: Verified Tier 2 tickets are present in CSV and Markdown.
9. `test_tier_1_shares_sum_to_100`: Verified Tier 1 closure shares sum to approximately 100.0% each week (range: 99.9% to 100.09%).
10. `test_rank_ordering_descending`: Verified rank ordering strictly tracks descending ticket volume.
11. `test_ties_handled_deterministically`: Verified tied volume receives identical rank with deterministic agent_id tie-breaker sorting.
12. `test_wow_calculation_with_zero_previous_volume`: Verified safe handling (NaN) when prior week count is zero.
13. `test_partial_weeks_flagged`: Verified incomplete weeks (e.g. `2025-W01`) are flagged `complete_week = False`.
14. `test_no_composite_performance_score`: Verified no arbitrary composite score columns exist.
15. `test_source_csvs_unmodified`: Verified all source CSVs in `data/` remain untouched.
16. `test_total_eligible_closures_reconciliation`: Verified total closures reconcile: 10,547 Tier 1 + 719 Tier 2 = 11,266.

---

## 8. Limitations & Operational Notes
- **Closure Date vs Creation Date:** In customer service operations, tickets closed per week are grouped by resolution date (`resolved_at_dt`), not ticket creation date (`created_at_dt`). In W26, 199 tickets were created and 192 tickets were closed.
- **Roster Snapshot:** All 44 agents currently feature ongoing assignments (`to_date = NaN`). The matching engine is built with interval logic ($\text{from\_date} \le \text{date} \le \text{to\_date}$) to gracefully support future multi-row roster updates.
- **Deterministic Production AI Statement:** All numbers, ranks, shares, and deltas were generated deterministically via Python with **0 external LLM calls**.
