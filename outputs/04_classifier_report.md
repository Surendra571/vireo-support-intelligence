# Vireo Audio — AI Ticket Classification Pipeline Report (Step 4 Quality Audit)

**Document Version:** 1.1.0  
**Pipeline Run Date:** 2026-10-02  
**Dataset Analyzed:** `data/tickets.csv` (11,875 unique clean customer support tickets)  
**Output Artifact:** `outputs/classified_tickets.csv` (11,875 rows, 100% coverage)  
**Validation Suite:** `pytest tests/` (52 passed in 36.00s)

---

## 1. Executive Summary & Purpose

The objective of Step 4 is to build a production-grade, AI-assisted ticket classification pipeline for Vireo Audio's 18 months of customer support data. 

The pipeline processes raw customer messages and agent resolution notes, combining them with ticket metadata (`product_sku`, `category`, `assigned_team`, `channel`) to produce standardized, machine-readable structured classifications. This structured data directly powers downstream business intelligence, thematic trend analysis, and the weekly operational digest (Step 5) without altering underlying ground-truth data or inventing unverified facts.

### Core Objectives
1. **Thematic Identification:** Map noisy, colloquial customer problem statements into a controlled, empirical issue taxonomy.
2. **Intent Recognition:** Categorize the customer's desired outcome (`request_technical_support`, `request_refund`, `request_replacement`, `request_delivery_status`, `request_invoice_billing`, `request_account_help`, `request_cancellation`, `general_inquiry`).
3. **Text-Based Repeat Signal Extraction:** Systematically flag explicit customer protests of prior unresolved contacts from message text.
4. **Resilience & Determinism:** Ensure 100% offline fallback capability, SQLite-backed persistent caching with WAL mode to prevent redundant computation, zero hallucination of financial/SLA metrics, and strict confidence bounds.

---

## 2. Controlled Taxonomy Design & Rationale

Rather than imposing a generic, off-the-shelf support taxonomy, Vireo Audio's taxonomy was empirically derived directly from the corpus of 11,875 support tickets, product catalog (`products.csv`), and operational team routing (`support-policy.pdf`).

### 2.1 Primary Issues (`primary_issue`)
The 16 controlled primary issue keys reflect real failure modes in consumer audio hardware, firmware, logistics, and billing:

| Primary Issue Key | Description & Scope | Empirical Frequency | Share (%) |
|:---|:---|---:|---:|
| `delivery_delayed_not_received` | Shipment delays, courier tracking stalls, undelivered parcels | 2,149 | 18.10% |
| `app_crash_bug` | Vireo companion mobile app crashing, sync failures, UI glitches | 1,522 | 12.82% |
| `bluetooth_pairing_failed` | BT disconnects, discovery failures, laptop/phone pairing rejection | 1,375 | 11.58% |
| `payment_failed_debited` | Double billing, checkout gateway failure, debited amount without order confirmation | 1,177 | 9.91% |
| `refund_not_credited` | Approved refund not reflecting in bank account/wallet after SLA window | 809 | 6.81% |
| `battery_drain_fast` | Premature battery discharge, failing to meet rated battery life specs | 785 | 6.61% |
| `audio_distortion_buzzing` | Static crackling, buzzing noise, high-frequency hiss, DSP distortion | 582 | 4.90% |
| `unknown` | Ambiguous text, insufficient context, unmapped category fallback | 547 | 4.61% |
| `account_login_issue` | OTP delivery failure, password reset loops, locked Vireo portal account | 516 | 4.35% |
| `earbud_not_charging` | Case pin misalignment, single earbud failing to charge in case | 506 | 4.26% |
| `hardware_physical_defect` | Broken headband, loose hinge, detached ear tip, cosmetic shell flaws | 491 | 4.13% |
| `general_product_inquiry` | Pre-purchase specs, compatibility questions, feature guidance | 399 | 3.36% |
| `cancellation_request` | Order cancellation requested before or during transit | 350 | 2.95% |
| `audio_silent_one_side` | Complete loss of sound in left or right channel | 286 | 2.41% |
| `damaged_in_transit` | Crushed retail box, water damage, broken hardware upon arrival | 195 | 1.64% |
| `mic_not_working` | Muffled microphone, call partner cannot hear voice, gain failure | 186 | 1.57% |
| **Total** | | **11,875** | **100.00%** |

---

## 3. Classification Method & Execution Transparency

In strict accordance with assessment integrity principles, this section documents the exact mechanism used to classify the 11,875 tickets.

### 3.1 Transparent Execution Audit
- **Underlying Provider:** Local Deterministic Rule-Based Engine (`RuleBasedTaxonomyClient`).
- **Internal Model Identifier:** `vireo-rule-based-engine-v1`.
- **Honest Provider Disclosure:** In this full-corpus run, **0 tickets were classified via external third-party LLM APIs** (neither `GEMINI_API_KEY` nor `OPENAI_API_KEY` was configured in the environment). The pipeline executed 100% deterministically using the built-in rule-based taxonomy engine. The identifier `vireo-rule-based-engine-v1` designates this local Python component and must not be confused with a remote generative language model.

### 3.2 Classification Method Distribution

| Classification Method | Technical Mechanism | Ticket Count | Share (%) |
|:---|:---|---:|---:|
| `rule_based_keyword` | Direct keyword and regex phrase matching against customer message | 7,474 | 62.94% |
| `category_fallback` | Deterministic mapping from ticket `category` when message is brief | 3,854 | 32.45% |
| `fallback_low_confidence` | Sparse text / unmapped category (`primary_issue = "unknown"`) | 547 | 4.61% |
| `llm_gemini` / `llm_openai` | External Generative LLM API Call | 0 | 0.00% |
| **Total** | | **11,875** | **100.00%** |

---

## 4. Text-Based Repeat Signals vs. Step 3 Baselines

A crucial methodological boundary is distinguishing **Text-Based Repeat Signals** from **Support Policy §10 Repeat Contacts**.

### 4.1 Text-Based Repeat Signals Definition & Volume
- **Text-Based Repeat Signals Count:** **1,457 tickets (12.27%)** out of 11,875.
- **Detection Method:** Case-insensitive regex pattern matching (`REPEAT_SIGNAL_PATTERNS`) on customer message text detecting explicit protest phrases (e.g., *"already contacted"*, *"told your colleague"*, *"still not fixed"*, *"reaching out again"*, *"second time contacting"*, *"following up on earlier"*, *"nobody helped"*).
- **Methodological Clarification:**  
  > [!NOTE]  
  > **This is a broader text-based detection measure than the 115-ticket Step 3 explicit-protest subset and should not be interpreted as the same population.**

### 4.2 Comprehensive Repeat Contact Context

| Metric Dimension | Text-Based Repeat Signals (Step 4) | Step 3 Method A (Strict Issue Proxy) | Step 3 Method B (Product Proxy) | Step 3 Explicit Protest Subset |
|:---|:---|:---|:---|:---|
| **Definition** | Customer message matches repeat protest regex | Same customer + same SKU + same category $\le$ 30d of resolution | Same customer + same SKU $\le$ 30d of resolution | Customer text contains exact protest phrases matched during Step 3 audit |
| **Data Source** | `customer_message` text regex | Relational event log timestamps & keys | Relational event log timestamps & keys | Curated text subset from Step 3 audit |
| **Ticket Count** | **1,457 tickets** | **1,412 tickets** | **3,270 tickets** | **115 tickets** |
| **Share of Corpus** | **12.27%** | **11.89%** | **27.54%** | **0.97%** |
| **Analytical Role** | Broad qualitative signal of customer repetition | Mathematical business goal baseline | Upper bound on product-level friction | Verified illustrative protest sample |

> [!WARNING]  
> **Boundary of Causality:**  
> Text-based repeat signals indicate **customer-reported repetition and perceived lack of resolution**. They provide qualitative evidence supporting investigations into premature closure and handover quality as operational hypotheses, but do **not** constitute proof of agent fault or ground-truth premature closure.

---

## 5. Customer Intent Sanity-Check & Quality Corrections

### 5.1 Intent Quality Diagnosis
An initial baseline implementation assigned `customer_intent = "general_inquiry"` to 5,254 tickets (44.24% of the corpus). Cross-tabulation revealed that thousands of tickets describing clear technical faults, payment debit failures, or missing deliveries were erroneously classified as general inquiry because they lacked narrow conversational triggers (e.g., customers writing *"battery drains very fast, barely lasts 2 hours"* without using the literal phrase *"how to fix"*).

### 5.2 Deterministic Refinements Implemented
The deterministic intent router was updated to evaluate text evidence across all functional support domains before defaulting to general inquiry:
1. **Technical Support (`request_technical_support`):** Added hardware defect and failure keywords (`drains`, `battery`, `crashes`, `closes itself`, `disconnect`, `buzzing`, `distortion`, `crackling`, `static`, `silent`, `no sound`, `mic`, `microphone`, `touch screen`, `lasts`).
2. **Delivery Status (`request_delivery_status`):** Added shipping status indicators (`not received`, `haven't received`, `hasn't arrived`, `still waiting`, `waiting for`, `dispatch`, `shipment`, `in transit`, `courier`, `delayed`).
3. **Invoice & Billing (`request_invoice_billing`):** Added transaction and checkout terms (`paid`, `charged`, `deducted`, `gateway failed`, `page failed`, `promo code`, `discount code`, `coupon`).
4. **Refunds (`request_refund`):** Added return logistics phrases (`amount not credited`, `pickup scheduled`, `reverse pickup`, `rescheduled pickup`, `nobody came for pickup`, `return was accepted`, `return pickup`).
5. **Account Help (`request_account_help`):** Added authentication phrases (`locked out`, `lockout`, `sign in`, `reset link`, `sent me a code`).

### 5.3 Customer Intent Distribution: Before vs. After

| Customer Intent Key | Initial Baseline Count | Initial Share (%) | Quality-Corrected Count | Corrected Share (%) | Net Change |
|:---|---:|---:|---:|---:|---:|
| `general_inquiry` | 5,254 | 44.24% | **2,827** | **23.81%** | -2,427 (-20.43 pp) |
| `request_technical_support` | 2,173 | 18.30% | **2,654** | **22.35%** | +481 (+4.05 pp) |
| `request_refund` | 1,496 | 12.60% | **2,290** | **19.28%** | +794 (+6.68 pp) |
| `request_delivery_status` | 704 | 5.93% | **1,488** | **12.53%** | +784 (+6.60 pp) |
| `request_invoice_billing` | 481 | 4.05% | **1,084** | **9.13%** | +603 (+5.08 pp) |
| `request_replacement` | 1,328 | 11.18% | **886** | **7.46%** | -442 (-3.72 pp) |
| `request_cancellation` | 281 | 2.37% | **376** | **3.17%** | +95 (+0.80 pp) |
| `request_account_help` | 158 | 1.33% | **270** | **2.27%** | +112 (+0.94 pp) |
| **Total** | **11,875** | **100.00%** | **11,875** | **100.00%** | — |

### 5.4 Primary Issue × Customer Intent Cross-Tabulation (% General Inquiry)

| Primary Issue | Total Tickets | Corrected General Inquiry Count | % General Inquiry | Operational Sanity Check |
|:---|---:|---:|---:|:---|
| `general_product_inquiry` | 399 | 226 | **56.64%** | Expected high GI share (pre-sale compatibility/specs) |
| `hardware_physical_defect` | 491 | 230 | **46.84%** | Customers reporting broken hinges asking what to do |
| `damaged_in_transit` | 195 | 77 | **39.49%** | Reduced from 65.13%; remaining ask general procedure |
| `unknown` | 547 | 193 | **35.28%** | Ambiguous/sparse tickets |
| `app_crash_bug` | 1,522 | 516 | **33.90%** | Reduced from 56.34%; technical support share increased |
| `audio_distortion_buzzing` | 582 | 193 | **33.16%** | Reduced from 53.78%; technical support share increased |
| `earbud_not_charging` | 506 | 178 | **35.18%** | Reduced from 49.11%; charging troubleshooting captured |
| `battery_drain_fast` | 785 | 199 | **25.35%** | **Massive improvement** (dropped from 62.47%) |
| `delivery_delayed_not_received` | 2,149 | 431 | **20.06%** | **Massive improvement** (dropped from 40.58%) |
| `audio_silent_one_side` | 286 | 55 | **19.23%** | Dropped from 60.84%; technical support captured |
| `bluetooth_pairing_failed` | 1,375 | 225 | **16.36%** | Dropped from 32.36%; pairing support captured |
| `refund_not_credited` | 809 | 129 | **15.95%** | **Massive improvement** (dropped from 36.09%) |
| `mic_not_working` | 186 | 28 | **15.05%** | Dropped from 58.06%; technical troubleshooting captured |
| `payment_failed_debited` | 1,177 | 131 | **11.13%** | **Massive improvement** (dropped from 30.76%) |
| `account_login_issue` | 516 | 16 | **3.10%** | **Massive improvement** (dropped from 26.36%) |
| `cancellation_request` | 350 | 0 | **0.00%** | 100% mapped to cancellation intent |

---

## 6. Confidence Tiers & Audit

All classifications are scored on a strict $[0.0, 1.0]$ confidence scale:

| Confidence Tier | Range | Ticket Count | Share (%) | Operational Definition |
|:---|:---:|---:|---:|:---|
| **High Confidence** | $\ge 0.80$ | 7,474 | 62.94% | Direct keyword / pattern match from customer message |
| **Medium Confidence** | $0.60 - 0.79$ | 3,854 | 32.45% | Category fallback when message text is brief |
| **Low Confidence** | $< 0.60$ | 547 | 4.61% | Unmapped / sparse input (`primary_issue = "unknown"`) |
| **Average Confidence** | — | — | **0.781** | Robust corpus-wide certainty |

---

## 7. Sample Classifications Across Major Domains

| Category | Ticket ID | SKU | Customer Message Snippet | Classified Issue | Classified Intent | Repeat Sig. | Method | Conf. |
|:---|:---:|:---:|:---|:---|:---|:---:|:---:|:---:|
| **Delivery & Shipping** | `TK-240001` | `VA-HP-ST3` | *"Order was placed 10 days ago and tracking has not moved..."* | `delivery_delayed_not_received` | `request_delivery_status` | `False` | `rule_based_keyword` | 0.85 |
| **Charging & Battery** | `TK-240007` | `VA-HP-ST3` | *"battery drains very fast, barely lasts 2 hours. please resolve."* | `battery_drain_fast` | `request_technical_support` | `False` | `rule_based_keyword` | 0.85 |
| **Connectivity** | `TK-240011` | `VA-EB-PL1` | *"helo cannot pair pulse 1 with my laptop pulse 1..."* | `bluetooth_pairing_failed` | `request_technical_support` | `False` | `rule_based_keyword` | 0.85 |
| **Billing & Payments** | `TK-240003` | `VA-SW-FIT` | *"the page failed after I paid and now nothing shows in my account..."* | `payment_failed_debited` | `request_invoice_billing` | `False` | `rule_based_keyword` | 0.85 |
| **Returns & Refunds** | `TK-240006` | `VA-EB-AIR` | *"Got airlite earbuds from Amazon 3 weeks back. Refund not received yet. Reaching out again..."* | `refund_not_credited` | `request_refund` | `True` | `rule_based_keyword` | 0.85 |

---

## 8. Remaining Limitations

1. **Ultra-Short Customer Messages:** 547 tickets (4.61%) have sparse text (e.g., *"not working"*, *"help"*). Without order or RMA linking, these remain classified as `unknown` with low confidence.
2. **Compound Customer Demands:** In tickets where a customer reports multiple distinct issues (e.g., pairing failure + battery drain), the single primary issue field prioritizes the first dominant technical signal.
3. **No Financial or SLA Inferences:** The classifier strictly avoids inferring SLA status, store credit amounts, or agent fault. These calculations remain 100% owned by the deterministic business analysis scripts.
