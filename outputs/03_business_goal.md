# Vireo Audio Support Intelligence — Business Goal Formulation (Step 3)
**Generated:** 2026-10-02 11:40:11 IST | **Status:** Mathematically Validated Candidates

## 1. Executive Baseline & Empirical Operating Metrics

Before defining any target, historical operations across 18 months (1 Jan 2025 – 30 Jun 2026; 6 quarters; 78 weeks) were measured against **Support Operating Policy v3.2**. Financial values are categorized by their exact accounting type:

| Operational Metric | 18-Month Baseline Volume | Baseline Rate | Baseline Financial Exposure (18-Month Total) | Quarterly Run-Rate | Financial Classification |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Total Support Tickets** | **11,875** | 100.0% | — | Mean: 150.32 tickets/wk | Operating Volume |
| **Repeat Contacts (Method A — Strict Issue)** | **1,412** | **11.89%** | **Rs 367,030** | **Rs 61,171.67** | Observed Contact Handling Cost |
| **Repeat Contacts (Method B — Product Proxy)** | **3,270** | **27.54%** | **Rs 878,120** | **Rs 146,353.33** | Observed Contact Handling Cost |
| **Explicit Repeat Complaints** | **115** | **0.97%** | — | ~19.2 complaints/qtr | Unresolved Resolution Signals |
| **First-Response SLA Breaches** | **1,051** | **8.85%** | **Rs 367,850** | **Rs 61,308.33** | Policy Store Credit Penalty Liability |
| **Internal Team Transfers** | **1,169** | **8.76%** | **Rs 356,545** | **Rs 59,424.17** | Benchmarked Re-handling Cost (Policy §4) |
| **Pulse 2 (`VA-EB-PL2`) Defect Outflow** | **3,401** | 86.14 / 100 orders | **Rs 2,172,861.00** | **Rs 362,143.50** | Fulfillment Outflow (Refunds + Replacements) |
| **Nexa 2 (`VA-SW-NX2`) Defect Outflow** | **1,253** | 94.28 / 100 orders | **Rs 1,695,359.00** | **Rs 282,559.83** | Fulfillment Outflow (Refunds + Replacements) |
| **Combined Flagship Defect Outflow** | **4,654** | 39.19% of tickets | **Rs 3,868,220.00** | **Rs 644,703.33** | Fulfillment Outflow (Refunds + Replacements) |

> [!IMPORTANT]

> **Accounting Boundary Rule:** Fundamental cost categories must never be summed into an arbitrary single 'savings' number. Observed contact handling costs (staffing capacity) reflect labor paid to answer channels; store credit penalties represent balance sheet credits; transfer benchmarks represent workflow friction; and fulfillment outflows represent physical cash refunds and inventory loss.

## 2. Candidate Goal Scenarios & Mathematical Derivations

All calculations strictly follow exact arithmetic: `quarterly_run_rate = 18_month_cost / 6`, `potential_avoided_cost = baseline_cost * reduction_pct`, `target_count = baseline_count * (1 - reduction_pct)`, and `quarterly_impact = potential_avoided_cost / 6`.

### Candidate Goal A — Repeat Contacts / First-Contact Resolution (FCR)

*Methodological Note:* Support Policy §10 defines FCR as no re-contact from the same customer regarding the *same issue* within 30 days. Because `issue_id` is absent, **Method A** operates as a strict issue proxy (same customer + SKU + category), whereas **Method B** operates as a product-level proxy (same customer + SKU) capturing multi-contact escalation journeys.

#### Method A Scenarios (Strict Issue Proxy):

| Scenario | Baseline Tickets | Target Tickets | Tickets Reduced | Potential Avoided Handling Cost (18m) | Quarterly Financial Impact | Annualized Financial Impact |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Reduce Method A by 10.0%** | 1,412 | approx. 1,271 | approx. 141 | Rs 36,703.0 | **Rs 6,117.17 / qtr** | **Rs 24,468.67 / yr** |
| **Reduce Method A by 20.0%** | 1,412 | approx. 1,130 | approx. 282 | Rs 73,406.0 | **Rs 12,234.33 / qtr** | **Rs 48,937.33 / yr** |
| **Reduce Method A by 30.0%** | 1,412 | approx. 988 | approx. 424 | Rs 110,109.0 | **Rs 18,351.5 / qtr** | **Rs 73,406.0 / yr** |

#### Method B Scenarios (Product Proxy — Upper Bound of Re-contacts for Same Device):

| Scenario | Baseline Tickets | Target Tickets | Tickets Reduced | Potential Avoided Handling Cost (18m) | Quarterly Financial Impact | Annualized Financial Impact |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Reduce Method B by 10.0%** | 3,270 | 2,943 | 327 | Rs 87,812.0 | **Rs 14,635.33 / qtr** | **Rs 58,541.33 / yr** |
| **Reduce Method B by 20.0%** | 3,270 | 2,616 | 654 | Rs 175,624.0 | **Rs 29,270.67 / qtr** | **Rs 117,082.67 / yr** |
| **Reduce Method B by 30.0%** | 3,270 | 2,289 | 981 | Rs 263,436.0 | **Rs 43,906.0 / qtr** | **Rs 175,624.0 / yr** |

### Candidate Goal B — First-Response SLA Breaches

*Operational Scope:* Modeled on reducing initial human response delays exceeding Support Policy §3 targets. Avoided costs represent store credit payouts not incurred.

| Scenario | Baseline Breaches | Target Breaches | Breaches Reduced | Store Credits Avoided (18m) | Quarterly Financial Impact | Annualized Financial Impact |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Reduce SLA Breaches by 10.0%** | 1,051 | approx. 946 | approx. 105 | Rs 36,785.0 | **Rs 6,130.83 / qtr** | **Rs 24,523.33 / yr** |
| **Reduce SLA Breaches by 20.0%** | 1,051 | approx. 841 | approx. 210 | Rs 73,570.0 | **Rs 12,261.67 / qtr** | **Rs 49,046.67 / yr** |
| **Reduce SLA Breaches by 30.0%** | 1,051 | approx. 736 | approx. 315 | Rs 110,355.0 | **Rs 18,392.5 / qtr** | **Rs 73,570.0 / yr** |

### Candidate Goal C — Internal Team Routing Transfers

*Policy Benchmark Note:* Support Policy §4 establishes a ₹305 re-handling cost per transfer. Reducing transfers reflects intake routing efficiency; however, ₹305 is an internal cost benchmark, not a direct cash ledger saving, and transfers to Tier 2 warranty specialists are structurally necessary.

| Scenario | Baseline Transfers | Target Transfers | Transfers Reduced | Benchmark Re-handling Cost Avoided | Quarterly Benchmark Impact | Annualized Benchmark Impact |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Reduce Transfers by 10.0%** | 1,169 | approx. 1,052 | approx. 117 | Rs 35,654.5 | **Rs 5,942.42 / qtr** | **Rs 23,769.67 / yr** |
| **Reduce Transfers by 20.0%** | 1,169 | approx. 935 | approx. 234 | Rs 71,309.0 | **Rs 11,884.83 / qtr** | **Rs 47,539.33 / yr** |
| **Reduce Transfers by 30.0%** | 1,169 | approx. 818 | approx. 351 | Rs 106,963.5 | **Rs 17,827.25 / qtr** | **Rs 71,309.0 / yr** |

### Candidate Goal D — Product Defect Fulfillment Outflow (Cross-Functional)

*Cross-Functional Limitation:* Product defect remediation requires hardware engineering and supplier intervention. Support operations alone cannot eliminate hardware manufacturing defects; support operations can only triage symptoms and provide telemetry.

| Product Scope | Reduction % | Baseline Outflow (18m) | Potential Outflow Reduction | Quarterly Outflow Impact | Annualized Outflow Impact |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Pulse 2 Only | 5.0% | Rs 2,172,861.0 | Rs 108,643.05 | Rs 18,107.17 / qtr | Rs 72,428.7 / yr |
| Pulse 2 Only | 10.0% | Rs 2,172,861.0 | Rs 217,286.1 | Rs 36,214.35 / qtr | Rs 144,857.4 / yr |
| Pulse 2 Only | 20.0% | Rs 2,172,861.0 | Rs 434,572.2 | Rs 72,428.7 / qtr | Rs 289,714.8 / yr |
| Nexa 2 Only | 5.0% | Rs 1,695,359.0 | Rs 84,767.95 | Rs 14,127.99 / qtr | Rs 56,511.97 / yr |
| Nexa 2 Only | 10.0% | Rs 1,695,359.0 | Rs 169,535.9 | Rs 28,255.98 / qtr | Rs 113,023.93 / yr |
| Nexa 2 Only | 20.0% | Rs 1,695,359.0 | Rs 339,071.8 | Rs 56,511.97 / qtr | Rs 226,047.87 / yr |
| **Combined (Pulse 2 + Nexa 2)** | **5.0%** | **Rs 3,868,220.0** | **Rs 193,411.0** | **Rs 32,235.17 / qtr** | **Rs 128,940.67 / yr** |
| **Combined (Pulse 2 + Nexa 2)** | **10.0%** | **Rs 3,868,220.0** | **Rs 386,822.0** | **Rs 64,470.33 / qtr** | **Rs 257,881.33 / yr** |
| **Combined (Pulse 2 + Nexa 2)** | **20.0%** | **Rs 3,868,220.0** | **Rs 773,644.0** | **Rs 128,940.67 / qtr** | **Rs 515,762.67 / yr** |

## 3. Evidence Strength & Limitations Matrix

In accordance with rigorous evidence-based principles, no subjective scores are assigned. The table below delineates the empirical basis and missing data for each candidate goal:

| Candidate Goal | Directly Observed | Calculated | Proxy Elements | Modeled Scenarios | Missing Data / Information Gap | Post-Deployment Measurement Requirement |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Goal A: Repeat Contacts (FCR)** | Timestamps (`created_at`, `resolved_at`), `customer_id`, channel | 30-day window difference, channel handling costs per Policy §4 | Category (Method A) or SKU (Method B) acts as issue proxy | 10%, 20%, 30% reduction in repeat handling capacity | No explicit `issue_id` in database schema | Tagging repeat contacts at intake; measuring return interval distribution |
| **Goal B: SLA Breaches** | `created_at`, `first_response_at`, channel | Difference in minutes vs Policy §3 threshold | Target minutes mapped from policy | 10%, 20%, 30% reduction in store credit liability | Resolution duration; agent shift schedules during breach hours | First-response timestamp tracking; queue waiting time monitoring |
| **Goal C: Internal Transfers** | Integer transfers count in helpdesk | ₹305 * transfers count | ₹305 policy benchmark represents friction | 10%, 20%, 30% reduction in transfer re-handling | Transfers unrecorded during legacy Freshdesk era; necessity flag | Tracking first-contact routing accuracy and transfer re-hops |
| **Goal D: Product Defect Outflow** | Refund amounts, replacement flags, SKU in orders | Normalized complaints per 100 orders, inventory + logistics replacement cost | Support complaint rate as proxy for true field defect rate | 5%, 10%, 20% reduction in cash outflow | Manufacturing batch codes; return physical inspection QA logs | Joint product-engineering defect remediation tracking; warranty claims |

## 4. Operational Alignment Between Proposed Tool & Metrics

The proposed AI support-intelligence system is designed to perform specific technical capabilities:
1. Classify customer messages at intake using a controlled taxonomy (primary issue, secondary issue, customer intent).
2. Identify repeat-contact signals directly from customer message text (e.g. protests of prior unresolved issues).
3. Surface emerging complaint themes and SKU concentrations in a deterministic weekly digest.
4. Track agent closure volumes while separating Tier 1 from Tier 2 specialists.

**Evidence-Based Alignment:**
- **The strongest alignment between the proposed tool and the observed operational metric is with Repeat Contacts / FCR (Candidate Goal A).**
  - *Mechanism:* 115 explicit customer protest messages provide direct evidence of unresolved/repeated-contact signals. These messages support investigating premature closure and handover quality as hypotheses, but do not establish causality. By identifying repeat contacts at intake and flagging unresolved issue clusters in the weekly digest, team leads can enforce diagnostic checklists before tickets are marked resolved.
  - *Controllability:* Support leadership controls frontline triage protocols, handover documentation standards, and queue routing directly.
- **Product Defect Outflows (Goal D)** represent the largest total financial exposure (₹3.87M on Pulse 2 and Nexa 2), but **support operations alone cannot control physical component failures**. The tool can only serve as an intelligence pipeline feeding hardware engineering and QA.

## 5. Proposed Defensible Business Goal Statements

Following the mandatory structure: *'Reduce [metric] from [baseline] to [target] within [time period], equivalent to approximately [N] fewer tickets/incidents and approximately ₹[X] in potential avoided [cost type] per quarter, subject to validation'*, three mathematically grounded options are proposed:


### Option 1 (Conservative — Strict Issue Proxy / Method A — 10% Reduction):

> **"Reduce Method A repeat contacts from 1,412 tickets (11.89% baseline) to 1,271 tickets (10.70% target) within two quarters (6 months) post-deployment, equivalent to approximately 141 fewer repeat tickets and approximately ₹6,117 in potential avoided handling cost per quarter (₹24,469 annualized), subject to operational validation."**

### Option 2 — 20% Reduction / 12-Month Validation Target:

> **"Reduce Method A repeat contacts from 1,412 tickets (11.89% baseline) to 1,130 tickets (9.51% target) within four quarters (12 months) post-deployment, equivalent to approximately 282 fewer repeat tickets and approximately ₹12,234 in potential avoided handling cost per quarter (₹48,937 annualized), subject to operational validation."**

### Option 3 (Pragmatic Operational Target — Product Proxy / Method B — 20% Reduction):

> **"Reduce Method B product-level repeat contacts from 3,270 tickets (27.54% baseline) to 2,616 tickets (22.03% target) within four quarters (12 months) post-deployment, equivalent to approximately 654 fewer re-contacts on the same device and approximately ₹29,271 in potential avoided handling cost per quarter (₹117,083 annualized), subject to operational validation."**

## 6. Post-Deployment Measurement Plan & Governance Guardrails

To verify whether the business goal is achieved without unintended negative consequences, the deployment must follow strict measurement protocols:


### Measurement Plan:

- **Historical Baseline:** 18-month clean ticket dataset (11,875 tickets; 1 Jan 2025 – 30 Jun 2026).
- **Intervention:** AI-assisted ticket triage, repeat-contact intake alerting, weekly digest issue clustering, and standardized diagnostic checklists.
- **Measurement Period:** 2 quarters (6 months) for interim review; 4 quarters (12 months) for annual goal audit.
- **Primary Metric:** Repeat-contact rate calculated under Method A (same customer + SKU + category <= 30 days) and Method B (same customer + SKU <= 30 days).
- **Secondary Metrics:**
  1. Mean days to re-contact (monitoring whether re-contacts are postponed past 30 days or genuinely resolved).
  2. CSAT response average and response rate on resolved tickets (verifying customer satisfaction improvement).
  3. First-response SLA breach rate by channel (ensuring triage does not slow initial response).
  4. Internal transfer frequency between Frontline and Tier 2 specialists.


### Essential Governance Guardrails:

1. **No Artificial Ticket Suppression:** Frontline agents must not discourage customers from contacting or fail to log tickets in order to artificially depress repeat counts.
2. **No Misleading Productivity Incentives:** Agent leaderboard metrics must explicitly separate Tier 1 from Tier 2. Tier 2 specialists must not be evaluated on closed-ticket velocity, as warranty investigations require detailed bench testing.
3. **Resolution Quality Auditing:** A ticket must not be marked 'resolved' unless all standardized diagnostic checklist items are satisfied and confirmed with the customer.
4. **No Premature Financial Booking:** Modeled potential avoided costs must remain clearly labeled as capacity savings until realized in reduced channel operating expenses.
