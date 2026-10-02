# Vireo Audio Support Intelligence — Business Problem Discovery & Analysis
**Generated:** 2026-10-01 22:13:08 IST | **Dataset:** Deduplicated Clean Tickets (11,875 records)

## Executive Summary

This quantitative discovery analysis examines 18 months of customer support operations (1 Jan 2025 – 30 Jun 2026) for Vireo Audio across 11,875 clean, deduplicated tickets. All financial calculations adhere strictly to **Support Operating Policy v3.2**.

### Key Measured Financial & Operational Outflows (18-Month Total):
1. **Customer Refunds (`FACT`):** **Rs 5,992,919.00** across 2,105 tickets.
2. **Product Replacements (`FACT`):** **1,202 units** issued (Rs 1,768,000 inventory cost + Rs 408,680 reverse logistics = **Rs 2,176,680.00**).
3. **Repeat Contact Handling Cost (`FACT`):** **Rs 878,120** (Product Proxy: Method B, 3,270 tickets) / **Rs 367,030** (Strict Issue Proxy: Method A, 1,412 tickets).
4. **First-Response SLA Store Credits (`FACT`):** **Rs 367,850** across 1,051 breached tickets (@ Rs 350 credit per policy §3).
5. **Observed Transfer Re-handling Benchmark (`FACT`):** **Rs 356,545** across 1,169 transfers (@ Rs 305 benchmark per policy §4).

## 1. Ticket Volume & Temporal Distribution

- **Total Deduplicated Tickets (`FACT`):** 11,875
- **Weekly Ticket Volume:** Mean = 150.32 tickets/week (Median = 171.0, Min = 46, Max = 240)
- **Temporal Trend (`FACT`):** Volume increased from 2,683 tickets in H1 2025 to 6,864 tickets in H1 2026 (+155.8% increase), concurrent with higher sales volume of Pulse 2 and Nexa 2.
- **Channel Breakdown (`FACT`):** Chat: 5,161 (43.46%), Email: 3,807 (32.06%), Voice: 1,704 (14.35%), Social: 1,203 (10.13%).

## 2. Category Distribution & Growth Trends

| Category | Total Tickets | Share (%) | H1 2025 Count | H1 2026 Count | Growth (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Delivery & Shipping** | 2,134 | 17.97% | 458 | 854 | **86.46%** |
| **Other** | 1,691 | 14.24% | 341 | 670 | **96.48%** |
| **Billing & Payments** | 1,624 | 13.68% | 324 | 601 | **85.49%** |
| **Returns & Refunds** | 1,197 | 10.08% | 226 | 464 | **105.31%** |
| **Connectivity** | 1,131 | 9.52% | 198 | 501 | **153.03%** |
| **Charging & Battery** | 955 | 8.04% | 165 | 448 | **171.52%** |
| **App & Firmware** | 822 | 6.92% | 146 | 384 | **163.01%** |
| **Audio Quality** | 792 | 6.67% | 140 | 371 | **165.0%** |
| **Warranty & Repair** | 620 | 5.22% | 116 | 259 | **123.28%** |
| **Product Enquiry** | 593 | 4.99% | 109 | 227 | **108.26%** |
| **Account & Login** | 316 | 2.66% | 52 | 140 | **169.23%** |

*Observation (`FACT`):* Hardware technical categories (Connectivity, Audio Quality, Charging & Battery) exhibited the largest absolute volume growth (+153% to +172%).

## 3. Product Complaint Normalization Against Orders

| Product Name | SKU | Orders | Tickets | Complaints / 100 Orders | Refunds (Rs) | Replacements | Fulfillment Outflow (Rs) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Nexa 2 Smartwatch** | `VA-SW-NX2` | 1,329 | 1,253 | **94.28** | Rs 1,363,349.00 | 119 | **Rs 1,695,359.00** |
| **Orbit Mini Speaker** | `VA-SP-MINI` | 951 | 845 | **88.85** | Rs 284,666.00 | 79 | **Rs 388,946.00** |
| **Pulse 2 True Wireless Earbuds** | `VA-EB-PL2` | 3,948 | 3,401 | **86.14** | Rs 1,557,701.00 | 338 | **Rs 2,172,861.00** |
| **Strata 3 Over-Ear Headphones** | `VA-HP-ST3` | 1,064 | 915 | **86.0** | Rs 769,063.00 | 85 | **Rs 1,023,213.00** |
| **Pulse Charging Case (spare)** | `VA-AC-CASE` | 305 | 248 | **81.31** | Rs 57,048.00 | 12 | **Rs 68,568.00** |
| **Nexa Fit Band** | `VA-SW-FIT` | 877 | 660 | **75.26** | Rs 198,196.00 | 77 | **Rs 289,826.00** |
| **AirLite Earbuds** | `VA-EB-AIR` | 1,423 | 1,030 | **72.38** | Rs 215,795.00 | 111 | **Rs 337,895.00** |
| **Pulse True Wireless Earbuds** | `VA-EB-PL1` | 2,102 | 1,518 | **72.22** | Rs 479,018.00 | 174 | **Rs 733,058.00** |
| **Arc Neckband** | `VA-NB-ARC` | 573 | 394 | **68.76** | Rs 54,890.00 | 46 | **Rs 95,370.00** |
| **65W GaN Charger** | `VA-AC-CH65` | 309 | 211 | **68.28** | Rs 57,592.00 | 16 | **Rs 72,792.00** |
| **Strata 2 Over-Ear Headphones** | `VA-HP-ST2` | 622 | 423 | **68.01** | Rs 284,639.00 | 40 | **Rs 382,239.00** |
| **Orbit Smart Speaker** | `VA-SP-ORB` | 752 | 503 | **66.89** | Rs 389,397.00 | 49 | **Rs 518,757.00** |
| **Nexa Smartwatch** | `VA-SW-NX1` | 602 | 384 | **63.79** | Rs 273,645.00 | 47 | **Rs 378,925.00** |
| **USB-C Braided Cable** | `VA-AC-CBL` | 143 | 90 | **62.94** | Rs 7,920.00 | 9 | **Rs 11,790.00** |

*Verified Product Concentration (`FACT`):*
- **Pulse 2 (`VA-EB-PL2`):** 3,401 tickets on 3,948 orders (**86.14 per 100 orders**). Total fulfillment outflow: **Rs 2,172,861.00** (Refunds: Rs 1,557,701.00 across 613 tickets; Replacements: 338 units = Rs 615,160.00).
- **Nexa 2 (`VA-SW-NX2`):** 1,253 tickets on 1,329 orders (**94.28 per 100 orders**). Total fulfillment outflow: **Rs 1,695,359.00** (Refunds: Rs 1,363,349.00 across 265 tickets; Replacements: 119 units = Rs 332,010.00).
- **Combined Pulse 2 & Nexa 2:** 4,654 tickets (**39.19% of all company tickets**), **Rs 2,921,050.00 in refunds** (48.74% of all company refunds), **457 replacements** (Rs 947,170.00). **Total combined verified outflow: Rs 3,868,220.00** (Quarterly run-rate: Rs 644,703.33/quarter).

## 4. Repeat Contacts & Transparent Methodology Comparison

Support Policy §10 defines: *'First-contact resolution = ticket resolved at first contact if the same customer does not contact again about the same issue within 30 days.'*

Because there is no explicit `issue_id` column in the database, we report 4 transparent, reproducible methods:

| Method | Definition | Repeat Tickets | Repeat Rate (%) | Observed Contact Cost (Rs) | Quarterly Run-Rate (Rs) | Explicit Complaints Detected | Limitations |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Method A — Strict Issue Proxy** | Same customer, same product/SKU, same category within 30 days of resolution. | **1,412** | **11.89%** | **Rs 367,030** | Rs 61,171.67 | **94/115 (81.74%)** | Category is an issue proxy, not ground truth, because agents may re-tag tickets upon closure. |
| **Method B — Product Proxy** | Same customer, same SKU within 30 days of resolution. | **3,270** | **27.54%** | **Rs 878,120** | Rs 146,353.33 | **98/115 (85.22%)** | Product-level repeat proxy, NOT exact same-issue detection. Captures cross-category escalation journeys. |
| **Method C — Text-Supported Issue Matching** | Same customer, within 30 days, same SKU, and token overlap Jaccard >= 0.15. | **908** | **7.65%** | **Rs 224,070** | Rs 37,345.00 | **37/115 (32.17%)** | Deterministic text similarity. Fails when customers write brief procedural follow-ups rather than re-explaining symptoms. |
| **Method D — Customer-Level Baseline** | Same customer contacts again within 30 days across any product or category. | **3,822** | **32.19%** | **Rs 1,030,450** | Rs 171,741.67 | **98/115 (85.22%)** | Upper bound of customer re-contact volume; includes unrelated subsequent inquiries. |

### Cost Breakdown by Channel for Repeat Methods:

- **Method A — Strict Issue Proxy:** Chat 639 (Rs 134,190), Email 490 (Rs 127,400), Voice 134 (Rs 69,680), Social 149 (Rs 35,760). Total Observed: **Rs 367,030**.

- **Method B — Product Proxy:** Chat 1,446 (Rs 303,660), Email 1,067 (Rs 277,420), Voice 412 (Rs 214,240), Social 345 (Rs 82,800). Total Observed: **Rs 878,120**.

- **Method C — Text-Supported Issue Matching:** Chat 449 (Rs 94,290), Email 323 (Rs 83,980), Voice 47 (Rs 24,440), Social 89 (Rs 21,360). Total Observed: **Rs 224,070**.

- **Method D — Customer-Level Baseline:** Chat 1,681 (Rs 353,010), Email 1,236 (Rs 321,360), Voice 496 (Rs 257,920), Social 409 (Rs 98,160). Total Observed: **Rs 1,030,450**.

### Potentially Avoidable Cost Scenarios (`ASSUMPTION` / Model):

We explicitly do NOT assume that 100% of repeat contacts are avoidable. Below are modeled reduction scenarios:
- **Method A (Strict Issue Proxy):** 20% reduction = **Rs 73,406.0**; 35% reduction = **Rs 128,460.5**; 50% reduction = **Rs 183,515.0**.
- **Method B (Product Proxy):** 20% reduction = **Rs 175,624.0**; 35% reduction = **Rs 307,342.0**; 50% reduction = **Rs 439,060.0**.

## 5. First-Response SLA Performance & Store Credit Liability

| Channel | Target | Tickets | Breaches | Breach (%) | Mean Response (mins) | Store Credit Liability (Rs) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Chat** | 15m | 5,161 | 424 | **8.22%** | 6.42m | **Rs 148,400** |
| **Voice Callback** | 120m | 1,704 | 96 | **5.63%** | 46.96m | **Rs 33,600** |
| **Social** | 240m | 1,203 | 91 | **7.56%** | 98.8m | **Rs 31,850** |
| **Email** | 480m | 3,807 | 440 | **11.56%** | 246.59m | **Rs 154,000** |
| **Voice** | 120m | 1,704 | 96 | **5.63%** | 46.96m | **Rs 33,600** |

*Total SLA Liability (`FACT`):* **1,051 tickets** breached (8.85%), incurring **Rs 367,850** in store credits (@ Rs 350 per breach).

## 6. Internal Transfers & Routing Friction

- **Total Transfers (`FACT`):** 1,169 across 1,040 tickets (8.76% transfer rate).
- **Observed Transfer Re-handling Benchmark (`FACT`):** **Rs 356,545** (@ Rs 305 per transfer benchmark per Support Policy §4).
- **Evidence Regarding Potential Reducibility (`FACT` & `HYPOTHESIS`):**
  - Chat Frontline initiated 377 transfers and Email Frontline initiated 235 transfers.
  - Transfers to Tier 2 Escalations & Warranty (360 tickets) represent legitimate escalation paths for physical defect verification.
  - `HYPOTHESIS`: Misclassification at intake (e.g. general inquiries that require Returns Desk) may account for a portion of frontline transfers; intake triage validation is needed to determine the exact reducible share.

## 7. Factual Comparison of Candidate Business Problems

Below is an objective, evidence-based evaluation of candidate business problems across empirical dimensions:


### CAND-01: Repeat Support Contacts & First-Contact Resolution (FCR) Breakdown

- **Observed Volume:** 3,270 tickets (Product Proxy: Method B) / 1,412 tickets (Strict Issue Proxy: Method A)
- **Observed Rate:** 27.54% (Method B) / 11.89% (Method A) of all support tickets
- **18-Month Cost:** Rs 878,120 (Method B) / Rs 367,030 (Method A) (Observed handling cost calculated using Support Policy §4 channel interaction rates)
- **Quarterly Run-Rate:** Rs 146,353.33/quarter (Method B) / Rs 61,171.67/quarter (Method A)
- **Observed Trend:** Upwards (+155.8% volume increase between H1 2025 and H1 2026 concurrent with overall ticket growth)
- **Concentration:** Returns Desk (35.5% repeat rate under Method B), Charging & Battery (32.6%), Pulse 2 earbuds (966 repeats under Method B)
- **Operational Controllability by Support:** High. Frontline diagnostic checklists, repeat alerts, and handover notes fall directly under support desk operations.
- **Evidence Quality:** High. Deterministic timestamp sequence tracking within 30-day window per Support Policy §10; validated by 115 explicit repeat complaint messages.
- **Measurement Limitations:** Lack of explicit issue_id in database requires proxy definitions. Not all repeat contacts are avoidable.
- **Working Hypotheses:** Hypothesis: premature closure and inconsistent handover notes may contribute to repeat contacts; the available ticket data does not establish causality.
- **Actionability:** Deploy automated repeat-contact banner alerts at intake and mandate diagnostic completion checklists before ticket resolution.

### CAND-02: Hardware Defect Outflows & Complaint Concentration in Flagship Products (Pulse 2 & Nexa 2)

- **Observed Volume:** 4,654 tickets combined (Pulse 2: 3,401 tickets; Nexa 2: 1,253 tickets)
- **Observed Rate:** 39.19% of all support tickets; 86.14 complaints per 100 orders on Pulse 2, 94.28 per 100 orders on Nexa 2
- **18-Month Cost:** Rs 3,868,220.00 combined (Refunds: Rs 2,921,050.00 across 878 tickets; Replacements: Rs 947,170.00 across 457 units) (Observed refunds from accounting records; replacement inventory unit cost plus policy logistics benchmark (Rs 340/unit))
- **Quarterly Run-Rate:** Rs 644,703.33/quarter
- **Observed Trend:** Upwards (+153% to +172% in hardware defect categories: Charging & Battery, Audio Quality, Connectivity)
- **Concentration:** Pulse 2 True Wireless Earbuds (Rs 2.17M outflow) and Nexa 2 Smartwatch (Rs 1.70M outflow). Represents 48.74% of all refund dollars.
- **Operational Controllability by Support:** Low to indirect. Support operations cannot fix manufacturing or firmware defects directly, but controls symptom telemetry and return qualification.
- **Evidence Quality:** High. Deterministic join between orders.csv and tickets.csv; verified accounting refund sums and replacement flags.
- **Measurement Limitations:** Detailed supplier manufacturing batch codes and return inspection logs are not in the dataset.
- **Working Hypotheses:** Hypothesis: hardware lot defects and Bluetooth companion app instability drive high complaint rates; factory QA logs are needed to verify root cause.
- **Actionability:** Provide structured defect telemetry to hardware engineering and implement interactive frontline pairing/charging triage to reduce false returns.

### CAND-03: First-Response SLA Breaches & Store Credit Liabilities

- **Observed Volume:** 1,051 breached tickets
- **Observed Rate:** 8.85% of eligible tickets
- **18-Month Cost:** Rs 367,850 (Exact policy-mandated liability: Rs 350 store credit per breach under Support Policy §3)
- **Quarterly Run-Rate:** Rs 61,308.33/quarter
- **Observed Trend:** Stable breach rate across quarters (7.8% to 11.2%), with highest breach rates in May-June 2026
- **Concentration:** Email Frontline has highest breach rate (11.56%, 440 breaches, Rs 154,000 credit liability)
- **Operational Controllability by Support:** High. Workforce shift scheduling, agent staffing, and queue routing are within support desk operational control.
- **Evidence Quality:** High. Exact timestamp differences between created_at and first_response_at compared to policy targets.
- **Measurement Limitations:** Measures only initial response; does not capture full resolution time or customer response delays.
- **Working Hypotheses:** Hypothesis: staffing imbalances across shifts and weekend queues may contribute to first-response breaches; schedule logs are needed to verify causality.
- **Actionability:** Rebalance agent shifts between Bengaluru and Indore; deploy automated 15-minute queue expiration alerts.

### CAND-04: Internal Team Routing Friction & Transfer Re-handling Benchmark Cost

- **Observed Volume:** 1,169 total transfers across 1,040 tickets
- **Observed Rate:** 8.76% of tickets transferred
- **18-Month Cost:** Rs 356,545 (Benchmarked re-handling cost: Rs 305 per transfer based on Support Policy §4)
- **Quarterly Run-Rate:** Rs 59,424.17/quarter
- **Observed Trend:** Concentrated in helpdesk period (transfers were not recorded in legacy_fd system)
- **Concentration:** Chat Frontline (377 transfers) and Email Frontline (235 transfers) transferring to Escalations & Warranty and Logistics
- **Operational Controllability by Support:** Moderate. Intake classification tags and automated routing rules can reduce misrouting.
- **Evidence Quality:** Moderate to High. Direct integer count from helpdesk transfers field; cost is benchmarked rather than direct ledger outflow.
- **Measurement Limitations:** Does not prove all transfers were unnecessary; transfers to Tier 2 are structurally required for warranty evaluations.
- **Working Hypotheses:** Hypothesis: customer misclassification at intake may increase transfer frequency; routing audit required to determine reducible share.
- **Actionability:** Deploy intake triage classifier to route warranty claims and shipping issues directly to specialist queues on first touch.

### CAND-05: Payment Gateway Debit Failures & Billing Refund Drain (DUP-PAYMENT)

- **Observed Volume:** 531 refund tickets
- **Observed Rate:** 4.47% of all tickets (25.23% of all refund tickets)
- **18-Month Cost:** Rs 1,461,223.00 (Directly observed refund payouts from accounting records)
- **Quarterly Run-Rate:** Rs 243,537.17/quarter
- **Observed Trend:** Consistent throughout 18 months, mirroring e-commerce transaction volume peaks
- **Concentration:** Billing Support team handles 100% of these cases; tickets typically have High or Urgent priority
- **Operational Controllability by Support:** Low for support desk (requires payment gateway engineering and webhook reconciliation); high for customer communication.
- **Evidence Quality:** High. Explicit refund reason code DUP-PAYMENT with exact refund amounts.
- **Measurement Limitations:** Payment gateway server logs are not in the support ticket dataset.
- **Working Hypotheses:** Hypothesis: webhook dropped events during payment gateway authorization lead to customer accounts being debited without order creation.
- **Actionability:** Escalate to payment gateway engineering for automated server-to-server transaction reconciliation.
