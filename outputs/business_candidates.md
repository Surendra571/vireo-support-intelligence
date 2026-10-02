# Vireo Audio — Candidate Business Problems & Evaluation
**Generated:** 2026-10-01 22:13:08 IST | **Status:** Factual Business Discovery

## Executive Introduction

This document provides an objective, evidence-based comparison of the candidate business problems discovered in the 18-month Vireo Audio support dataset (11,875 clean tickets). No subjective weighting formula or unverified causal claims are applied. All metrics are derived from deterministic calculations against Support Operating Policy v3.2.

## Candidate Evaluation Template

### CAND-01: Repeat Support Contacts & First-Contact Resolution (FCR) Breakdown

- **Observed Volume:** 3,270 tickets (Product Proxy: Method B) / 1,412 tickets (Strict Issue Proxy: Method A)
- **Observed Rate:** 27.54% (Method B) / 11.89% (Method A) of all support tickets
- **18-Month Financial Exposure:** Rs 878,120 (Method B) / Rs 367,030 (Method A)
- **Quarterly Run-Rate:** Rs 146,353.33/quarter (Method B) / Rs 61,171.67/quarter (Method A)
- **Cost Classification:** Observed handling cost calculated using Support Policy §4 channel interaction rates
- **Observed Trend:** Upwards (+155.8% volume increase between H1 2025 and H1 2026 concurrent with overall ticket growth)
- **Concentration:** Returns Desk (35.5% repeat rate under Method B), Charging & Battery (32.6%), Pulse 2 earbuds (966 repeats under Method B)
- **Support Desk Controllability:** High. Frontline diagnostic checklists, repeat alerts, and handover notes fall directly under support desk operations.
- **Evidence Quality:** High. Deterministic timestamp sequence tracking within 30-day window per Support Policy §10; validated by 115 explicit repeat complaint messages.
- **Measurement Limitations:** Lack of explicit issue_id in database requires proxy definitions. Not all repeat contacts are avoidable.
- **Working Hypotheses:** Hypothesis: premature closure and inconsistent handover notes may contribute to repeat contacts; the available ticket data does not establish causality.
- **Actionability:** Deploy automated repeat-contact banner alerts at intake and mandate diagnostic completion checklists before ticket resolution.

### CAND-02: Hardware Defect Outflows & Complaint Concentration in Flagship Products (Pulse 2 & Nexa 2)

- **Observed Volume:** 4,654 tickets combined (Pulse 2: 3,401 tickets; Nexa 2: 1,253 tickets)
- **Observed Rate:** 39.19% of all support tickets; 86.14 complaints per 100 orders on Pulse 2, 94.28 per 100 orders on Nexa 2
- **18-Month Financial Exposure:** Rs 3,868,220.00 combined (Refunds: Rs 2,921,050.00 across 878 tickets; Replacements: Rs 947,170.00 across 457 units)
- **Quarterly Run-Rate:** Rs 644,703.33/quarter
- **Cost Classification:** Observed refunds from accounting records; replacement inventory unit cost plus policy logistics benchmark (Rs 340/unit)
- **Observed Trend:** Upwards (+153% to +172% in hardware defect categories: Charging & Battery, Audio Quality, Connectivity)
- **Concentration:** Pulse 2 True Wireless Earbuds (Rs 2.17M outflow) and Nexa 2 Smartwatch (Rs 1.70M outflow). Represents 48.74% of all refund dollars.
- **Support Desk Controllability:** Low to indirect. Support operations cannot fix manufacturing or firmware defects directly, but controls symptom telemetry and return qualification.
- **Evidence Quality:** High. Deterministic join between orders.csv and tickets.csv; verified accounting refund sums and replacement flags.
- **Measurement Limitations:** Detailed supplier manufacturing batch codes and return inspection logs are not in the dataset.
- **Working Hypotheses:** Hypothesis: hardware lot defects and Bluetooth companion app instability drive high complaint rates; factory QA logs are needed to verify root cause.
- **Actionability:** Provide structured defect telemetry to hardware engineering and implement interactive frontline pairing/charging triage to reduce false returns.

### CAND-03: First-Response SLA Breaches & Store Credit Liabilities

- **Observed Volume:** 1,051 breached tickets
- **Observed Rate:** 8.85% of eligible tickets
- **18-Month Financial Exposure:** Rs 367,850
- **Quarterly Run-Rate:** Rs 61,308.33/quarter
- **Cost Classification:** Exact policy-mandated liability: Rs 350 store credit per breach under Support Policy §3
- **Observed Trend:** Stable breach rate across quarters (7.8% to 11.2%), with highest breach rates in May-June 2026
- **Concentration:** Email Frontline has highest breach rate (11.56%, 440 breaches, Rs 154,000 credit liability)
- **Support Desk Controllability:** High. Workforce shift scheduling, agent staffing, and queue routing are within support desk operational control.
- **Evidence Quality:** High. Exact timestamp differences between created_at and first_response_at compared to policy targets.
- **Measurement Limitations:** Measures only initial response; does not capture full resolution time or customer response delays.
- **Working Hypotheses:** Hypothesis: staffing imbalances across shifts and weekend queues may contribute to first-response breaches; schedule logs are needed to verify causality.
- **Actionability:** Rebalance agent shifts between Bengaluru and Indore; deploy automated 15-minute queue expiration alerts.

### CAND-04: Internal Team Routing Friction & Transfer Re-handling Benchmark Cost

- **Observed Volume:** 1,169 total transfers across 1,040 tickets
- **Observed Rate:** 8.76% of tickets transferred
- **18-Month Financial Exposure:** Rs 356,545
- **Quarterly Run-Rate:** Rs 59,424.17/quarter
- **Cost Classification:** Benchmarked re-handling cost: Rs 305 per transfer based on Support Policy §4
- **Observed Trend:** Concentrated in helpdesk period (transfers were not recorded in legacy_fd system)
- **Concentration:** Chat Frontline (377 transfers) and Email Frontline (235 transfers) transferring to Escalations & Warranty and Logistics
- **Support Desk Controllability:** Moderate. Intake classification tags and automated routing rules can reduce misrouting.
- **Evidence Quality:** Moderate to High. Direct integer count from helpdesk transfers field; cost is benchmarked rather than direct ledger outflow.
- **Measurement Limitations:** Does not prove all transfers were unnecessary; transfers to Tier 2 are structurally required for warranty evaluations.
- **Working Hypotheses:** Hypothesis: customer misclassification at intake may increase transfer frequency; routing audit required to determine reducible share.
- **Actionability:** Deploy intake triage classifier to route warranty claims and shipping issues directly to specialist queues on first touch.

### CAND-05: Payment Gateway Debit Failures & Billing Refund Drain (DUP-PAYMENT)

- **Observed Volume:** 531 refund tickets
- **Observed Rate:** 4.47% of all tickets (25.23% of all refund tickets)
- **18-Month Financial Exposure:** Rs 1,461,223.00
- **Quarterly Run-Rate:** Rs 243,537.17/quarter
- **Cost Classification:** Directly observed refund payouts from accounting records
- **Observed Trend:** Consistent throughout 18 months, mirroring e-commerce transaction volume peaks
- **Concentration:** Billing Support team handles 100% of these cases; tickets typically have High or Urgent priority
- **Support Desk Controllability:** Low for support desk (requires payment gateway engineering and webhook reconciliation); high for customer communication.
- **Evidence Quality:** High. Explicit refund reason code DUP-PAYMENT with exact refund amounts.
- **Measurement Limitations:** Payment gateway server logs are not in the support ticket dataset.
- **Working Hypotheses:** Hypothesis: webhook dropped events during payment gateway authorization lead to customer accounts being debited without order creation.
- **Actionability:** Escalate to payment gateway engineering for automated server-to-server transaction reconciliation.

## Comparative Evaluation Matrix

| Dimension | Candidate 1: Repeat Contacts (Method B / Method A) | Candidate 2: Flagship Hardware Defects (Pulse 2 & Nexa 2) | Candidate 3: First-Response SLA Breaches | Candidate 4: Team Transfer Routing Friction | Candidate 5: Payment Gateway Failures (DUP-PAYMENT) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Observed Volume** | 3,270 tickets (B) / 1,412 (A) | 4,654 tickets | 1,051 breached tickets | 1,169 total transfers across 1,040 tickets | 531 refund tickets |
| **Operational Rate** | 27.54% (B) / 11.89% (A) of tickets | 39.19% of tickets; 86.1% to 94.3% of orders | 8.85% of eligible tickets | 8.76% of tickets transferred | 4.47% of all tickets (25.23% of all refund tickets) |
| **18-Month Cost** | **Rs 878,120 (B) / Rs 367,030 (A)** | **Rs 3,868,220.00** | **Rs 367,850** | **Rs 356,545** | **Rs 1,461,223** |
| **Quarterly Run-Rate** | Rs 146,353 (B) / Rs 61,172 (A) | Rs 644,703 / quarter | Rs 61,308 / quarter | Rs 59,424 / quarter | Rs 243,537 / quarter |
| **Cost Type** | Observed handling cost | Observed refunds + verified replacement costs | Policy store credit penalties | Benchmarked re-handling cost | Observed customer refunds |
| **Trend** | Upwards (+155.8%) | Upwards (+153% to +172% defect categories) | Stable (7.8% - 11.2%) | Flat | Flat (4% - 5%) |
| **Concentration** | Returns Desk (35.5%), Pulse 2 (966) | Pulse 2 (56.2% of defect cost) | Email Frontline (11.56%) | Chat & Email Frontline | Billing Support (100%) |
| **Controllability** | **High** (Support Desk SOPs & Intake) | **Low to Indirect** (Cross-functional) | **High** (Queue Management) | **Moderate** (Intake Routing) | **Low** (FinTech / Webhooks) |
| **Evidence Quality** | High (Policy §10 temporal window + 115 explicit complaints) | High (Order join + verified SKU accounting) | High (Exact timestamp calculation) | High (Helpdesk transfer counter) | High (Accounting reason code DUP-PAYMENT) |
| **Actionability** | Triage checklists, repeat alerts, handover notes | Symptom telemetry, pairing reset guides | Staffing rebalance, queue alerts | Direct routing rules | Gateway webhook reconciliation |

## Synthesis of Candidate Findings

The quantitative evidence establishes two distinct, high-impact business problem candidates with sufficient empirical evidence to investigate further:

1. **Operational Support Candidate — Repeat Contacts & FCR Breakdown (Candidate 1):**
   - **Empirical Scale:** 1,412 tickets (Strict Issue Proxy) to 3,270 tickets (Product Proxy), with observed contact handling costs between **Rs 367,030** and **Rs 878,120**.
   - **Operational Controllability:** High. Support desk processes (diagnostic completion, repeat alerts, structured notes) directly govern frontline re-contact rates.
   - **Avoidable Potential:** Modeled 20% to 35% reduction offers Rs 73,400 to Rs 307,300 in capacity savings without adding agent headcount.

2. **Product Quality & Intelligence Candidate — Flagship Hardware Defect Outflows (Candidate 2):**
   - **Empirical Scale:** 4,654 tickets across Pulse 2 and Nexa 2, generating **Rs 3,868,220.00** in verified refunds and replacements (47.35% of all company fulfillment outflows).
   - **Operational Controllability:** Cross-functional. While support cannot repair hardware in the field, support intelligence provides immediate root-cause telemetry to engineering.
