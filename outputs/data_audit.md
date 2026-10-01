# Vireo Audio Support Intelligence — Data Audit & Profiling Report
**Generated:** 2026-10-01T19:33:03.505272+05:30 | **Standard Timezone:** Asia/Kolkata (IST)

## Executive Summary

This data audit profiles all 5 source CSV datasets (`tickets.csv`, `orders.csv`, `customers.csv`, `products.csv`, `agents.csv`), validates referential integrity, parses timestamps into IST, and rigorously assesses compliance against **Vireo Support Operating Policy v3.2**.

> [!IMPORTANT]
> **Key Takeaway:** The data contains **653 re-imported duplicate tickets** (1,306 rows) between the legacy Freshdesk and helpdesk systems, and **2,263 legacy tickets with UTC-reconstructed timestamps** causing inverted resolution times. Neither of these issues should be silently modified in source data, but both must be explicitly accounted for during analysis.

## 1. Dataset Profiles Overview

| Dataset | Rows | Columns | Duplicate Rows | Primary / Important Key | Unique Keys | Missing Values (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `tickets.csv` | 12,528 | 21 | 0 | `ticket_id` | 11,875 | up to 82.24% |
| `agents.csv` | 44 | 8 | 0 | `agent_id` | 44 | up to 100.0% |
| `customers.csv` | 9,500 | 6 | 0 | `customer_id` | 9,500 | up to 0.0% |
| `orders.csv` | 15,000 | 8 | 0 | `order_id` | 15,000 | up to 0.0% |
| `products.csv` | 14 | 7 | 0 | `sku` | 14 | up to 0.0% |


## 2. Categorized Findings

### 2.1 Confirmed Data Problems

#### [PROB-001] Duplicate / Re-imported Legacy Tickets in Helpdesk Export (HIGH Severity)
- **Affected Records:** 1,306
- **Finding:** There are 653 ticket IDs appearing twice in tickets.csv (total 1306 rows) across source_system values 'helpdesk' and 'legacy_fd'. These tickets were originally created in Freshdesk (Jan 2025 – Sep 2025) and re-imported into the new helpdesk during system migration reconciliation. Downstream aggregations will double-count volume, SLA breaches, and financial metrics if not deduplicated.

#### [PROB-002] Timezone Inconsistency in Legacy Resolution Timestamps (UTC vs IST) (HIGH Severity)
- **Affected Records:** 2,263
- **Finding:** 2263 tickets in 'legacy_fd' have resolved_at timestamps earlier than created_at (and 2,472 earlier than first_response_at). As confirmed by Support Policy §9 and IT email communications, legacy resolution timestamps were reconstructed from raw event logs recorded in UTC, while created_at and first_response_at are in IST (UTC+05:30). Adding +05:30 to legacy resolved_at eliminates 100% of negative resolution durations.

#### [PROB-003] Policy Violation: Simultaneous Refund and Replacement Issued (MEDIUM Severity)
- **Affected Records:** 4
- **Finding:** 4 tickets have both a monetary refund (>0) and replacement_issued='Y' on the same ticket. Furthermore, 103 orders have both a refund and a replacement issued across distinct tickets. Support Policy §5 explicitly states: 'In no case is a customer to receive both a refund and a replacement for the same order'.

#### [PROB-004] Policy Violation: Goodwill Refunds Exceeding Rs 500 Cap (MEDIUM Severity)
- **Affected Records:** 38
- **Finding:** 38 out of 44 goodwill refunds (code 'GW-OTHER') exceed the Rs 500 cap mandated by Support Policy §5. The average goodwill refund for these breached tickets is Rs 2,972 (maximum Rs 10,798).

#### [PROB-005] Policy Violation: Tier 1 Agents Approving Warranty & Repair Replacements (LOW Severity)
- **Affected Records:** 8
- **Finding:** 8 warranty replacements were resolved and approved by Tier 1 agents. Support Policy §6 states that Tier 2 work is certified and only Tier 2 agents (Escalations & Warranty) may approve warranty replacements.

### 2.2 Expected Behaviors (According to Support Policy)

#### [EXP-001] Missing resolved_at on Open and Pending Tickets
- **Observation:** Exactly 644 tickets have null resolved_at. Every single one corresponds to an open (399) or pending (245) ticket. Zero resolved/closed tickets are missing resolved_at.

#### [EXP-002] Missing order_id on 33.7% of Support Tickets
- **Observation:** 4218 tickets (33.67%) have null order_id. Per README and operational reality, customers frequently contact support without providing their order number.

#### [EXP-003] Missing and Zero CSAT Survey Scores
- **Observation:** 4,856 tickets have null CSAT scores (helpdesk format) and 2,083 tickets have CSAT=0.0 (legacy format). Support Policy §8 states survey response rate is ~45% and unrated surveys must be excluded from averages, not treated as 0.

#### [EXP-004] Missing Refund Fields on Non-Refund Tickets
- **Observation:** 10,303 tickets (82.2%) have null refund_amount_inr and refund_reason_code. This is expected as refunds are only issued on eligible return/warranty/cancellation claims.

#### [EXP-005] Null to_date in Agents Roster
- **Observation:** All 44 agents have to_date as null, reflecting active current assignments.

### 2.3 Items Requiring Investigation

#### [INV-001] Fallback Join Disambiguation for Missing order_id (customer_id + product_sku)
- **Analysis:** Of 4218 tickets missing order_id, 3,467 (82.2%) match exactly 1 order in orders.csv. However, 751 tickets (17.8%) match multiple historical orders for that customer and SKU (651 match 2 orders, 84 match 3, 16 match 4). A deterministic disambiguation rule (e.g. nearest prior order_date) is required.

#### [INV-002] Deduplication Strategy for Downstream Analysis
- **Analysis:** For the 653 duplicated tickets, downstream models must decide whether to retain the 'helpdesk' or 'legacy_fd' record. The helpdesk record provides IST resolved_at and null CSAT, whereas legacy_fd provides reconstructed UTC resolved_at and 0.0 CSAT. The recommended policy is retaining the 'helpdesk' record (or migrating/correcting legacy timestamps).

#### [INV-003] High Refund Volume Processed Outside Returns Desk
- **Analysis:** Support Policy §6 states Returns Desk processes the large majority of refunds by design. In practice, Billing processed 695 refunds (Rs 1,821,356) and Frontline/Logistics teams processed 727 refunds (Rs 2,141,222), while Returns Desk processed 669 refunds (Rs 1,982,247). Operational routing should be reviewed.

#### [INV-004] Agent Assignment Roster Multi-Row Safety
- **Analysis:** While agents.csv currently has 44 unique agent_ids, future roster updates with shift or site changes will introduce duplicate agent_id rows with historical to_date. Pipelines must join on (agent_id, ticket_created_at BETWEEN from_date AND to_date).

## 3. Deep-Dive Investigations

### 3.1 Legacy Freshdesk Re-import Reconciliation

- **Total Duplicated Ticket IDs:** 653 (1,306 total rows)
- **Source Distribution:** 653 in `helpdesk` vs 653 in `legacy_fd`
- **Creation Window:** 2025-01-01 09:48:00 to 2025-09-14 04:23:00
- **Field Differences between Duplicates:**
  - `resolved_at`: 618 tickets differ by exactly 5 hours 30 minutes (UTC vs IST).
  - `csat_score`: 333 tickets differ where legacy recorded `0.0` and helpdesk recorded blank (`NaN`).
  - All other 17 columns (`created_at`, `first_response_at`, `category`, `customer_id`, `order_id`, `product_sku`, etc.) are **100% identical**.

### 3.2 Order ID Fallback Join Analysis (`customer_id` + `product_sku`)

- **Tickets with missing `order_id`:** 4,218 (33.67%)
- **Deterministic Unique Matches (1-to-1):** 3,467 (82.2%)
- **Ambiguous Multi-Order Matches (>1):** 751 (17.8%)
  - 2 matching orders: 651 tickets
  - 3 matching orders: 84 tickets
  - 4 matching orders: 16 tickets
- **Orphan Fallback Matches (0 matches):** 0 (0.0% — every ticket has at least one valid customer order!)
- **Integrity of existing `order_id`:** 8,310 tickets with order_id were checked against `orders.csv`: **0 customer mismatches** and **0 SKU mismatches**.

### 3.3 Agents Roster Structure

- **Total Roster Entries:** 44 rows (44 unique `agent_id` values, all with `to_date = NaN`).
- **Important Operational Nuance:** Roster represents assignment periods (`from_date` to `to_date`). Agents shifting between sites (Bengaluru/Indore) or teams receive a new roster row with the same `agent_id`. While 1-to-1 in this snapshot, models must avoid naive unique-key assumptions.

## 4. Referential Integrity Matrix

| Relationship | FK Type | Status | Orphan Count |
| :--- | :--- | :--- | :--- |
| `tickets.customer_id -> customers.customer_id` | Many-to-One | PASSED | 0 |
| `tickets.order_id -> orders.order_id (non-null)` | Many-to-One | PASSED | 0 |
| `tickets.product_sku -> products.sku` | Many-to-One | PASSED | 0 |
| `tickets.agent_id -> agents.agent_id` | Many-to-One | PASSED | 0 |
| `orders.customer_id -> customers.customer_id` | Many-to-One | PASSED | 0 |
| `orders.sku -> products.sku` | Many-to-One | PASSED | 0 |

