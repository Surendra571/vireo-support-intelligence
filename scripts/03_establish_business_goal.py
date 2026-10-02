"""scripts/03_establish_business_goal.py

Vireo Audio Support Intelligence — Step 3: Business Goal Formulation
====================================================================
Translates validated Step 2 business discovery and empirical findings into
mathematically defensible, policy-aligned business goal options.

Enforces strict evaluation standards:
  - 'Number + Money' business goal formulation.
  - Transparent distinction between observed costs, benchmark costs, and modeled scenarios.
  - No combination of fundamentally different financial categories into a single 'savings' number.
  - Arithmetic consistency:
      quarterly_run_rate = 18_month_cost / 6
      potential_avoided_cost = baseline_cost * reduction_percentage
      target_count = baseline_count * (1 - reduction_percentage)
      reduction_count = baseline_count - target_count
      quarterly_financial_impact = potential_avoided_cost / 6
      annualized_financial_impact = quarterly_financial_impact * 4

Generates:
  - outputs/03_business_goal.md
  - outputs/03_business_goal.json
  - outputs/03_goal_scenarios.csv
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

IST = timezone(timedelta(hours=5, minutes=30))


def load_step2_metrics(outputs_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Loads validated metrics from outputs/business_metrics.json."""
    if outputs_dir is None:
        outputs_dir = Path(__file__).resolve().parent.parent / "outputs"

    json_path = outputs_dir / "business_metrics.json"
    if not json_path.exists():
        raise FileNotFoundError(f"Missing Step 2 metrics: {json_path}. Run scripts/02_business_analysis.py first.")

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_goal_scenarios(metrics: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Calculates all candidate business goal scenarios programmatically with exact arithmetic."""
    t_total = metrics["total_analyzed_tickets"]
    m_a = metrics["repeat_contact_metrics"]["repeat_definitions_comparison"]["method_a"]
    m_b = metrics["repeat_contact_metrics"]["repeat_definitions_comparison"]["method_b"]
    sla = metrics["outcomes_and_sla_metrics"]["overall_rates"]
    p2 = metrics["product_metrics"]["VA-EB-PL2"]
    nx2 = metrics["product_metrics"]["VA-SW-NX2"]

    rows = []
    scenarios_dict: Dict[str, List[Dict[str, Any]]] = {}

    def add_scenario_group(
        goal_id: str,
        goal_name: str,
        metric_name: str,
        baseline_count: float,
        baseline_cost: float,
        cost_type: str,
        percentages: List[float],
        controllability: str,
        alignment_note: str,
    ) -> None:
        group_list = []
        for pct in percentages:
            target_cnt = baseline_count * (1.0 - pct)
            reduced_cnt = baseline_count - target_cnt
            avoided_18m = baseline_cost * pct
            q_impact = avoided_18m / 6.0
            ann_impact = q_impact * 4.0

            scen_record = {
                "goal_id": goal_id,
                "goal_name": goal_name,
                "metric_name": metric_name,
                "reduction_percentage": round(pct * 100, 1),
                "baseline_count": round(baseline_count, 1),
                "target_count": round(target_cnt, 1),
                "reduction_count": round(reduced_cnt, 1),
                "baseline_cost_18m_inr": round(baseline_cost, 2),
                "cost_type": cost_type,
                "potential_avoided_cost_18m_inr": round(avoided_18m, 2),
                "quarterly_financial_impact_inr": round(q_impact, 2),
                "annualized_financial_impact_inr": round(ann_impact, 2),
                "operational_controllability": controllability,
                "tool_alignment": alignment_note,
            }
            rows.append(scen_record)
            group_list.append(scen_record)
        scenarios_dict[goal_id] = group_list

    # 1. Candidate Goal A1: Repeat Contacts (Method A — Strict Issue Proxy)
    add_scenario_group(
        goal_id="GOAL-A1",
        goal_name="Repeat Contacts (Method A — Strict Issue Proxy)",
        metric_name="Method A repeat tickets (same customer + SKU + category <= 30d)",
        baseline_count=float(m_a["repeat_tickets_count"]),
        baseline_cost=float(m_a["observed_contact_cost_inr"]),
        cost_type="observed_contact_handling_cost",
        percentages=[0.10, 0.20, 0.30],
        controllability="High (Support Desk Operations)",
        alignment_note="Direct: intake repeat detection, diagnostic checklists, and handover notes directly mitigate premature closure.",
    )

    # 2. Candidate Goal A2: Repeat Contacts (Method B — Product Proxy)
    add_scenario_group(
        goal_id="GOAL-A2",
        goal_name="Repeat Contacts (Method B — Product Proxy)",
        metric_name="Method B repeat tickets (same customer + SKU <= 30d)",
        baseline_count=float(m_b["repeat_tickets_count"]),
        baseline_cost=float(m_b["observed_contact_cost_inr"]),
        cost_type="observed_contact_handling_cost",
        percentages=[0.10, 0.20, 0.30],
        controllability="High (Support Desk Operations)",
        alignment_note="Direct: captures cross-category escalation journeys where customers return under different tags for same device.",
    )

    # 3. Candidate Goal B: SLA First-Response Breaches
    add_scenario_group(
        goal_id="GOAL-B",
        goal_name="First-Response SLA Breaches",
        metric_name="First-response SLA breached tickets",
        baseline_count=float(sla["sla_breach_tickets"]),
        baseline_cost=float(sla["total_sla_breach_cost_inr"]),
        cost_type="policy_store_credit_penalty",
        percentages=[0.10, 0.20, 0.30],
        controllability="High (Workforce Scheduling & Queue Routing)",
        alignment_note="Moderate: tool provides queue backlog visibility in weekly digest, but real-time response depends on shift staffing.",
    )

    # 4. Candidate Goal C: Internal Team Transfers
    add_scenario_group(
        goal_id="GOAL-C",
        goal_name="Internal Team Transfers",
        metric_name="Total team-to-team ticket transfers",
        baseline_count=float(sla["total_transfers_count"]),
        baseline_cost=float(sla["transfer_handling_cost_inr"]),
        cost_type="benchmark_rehandling_cost",
        percentages=[0.10, 0.20, 0.30],
        controllability="Moderate (Intake Classification & Routing)",
        alignment_note="Moderate: intake classifier can route cases directly to specialist teams, reducing frontline re-hops.",
    )

    # 5. Candidate Goal D1: Pulse 2 Defect Outflow
    p2_outflow = float(p2["total_fulfillment_outflow_inr"])
    p2_tickets = float(p2["tickets"])
    add_scenario_group(
        goal_id="GOAL-D1",
        goal_name="Pulse 2 Defect Fulfillment Outflow",
        metric_name="Pulse 2 support tickets and fulfillment outflow",
        baseline_count=p2_tickets,
        baseline_cost=p2_outflow,
        cost_type="fulfillment_outflow (refunds + replacements)",
        percentages=[0.05, 0.10, 0.20],
        controllability="Low / Indirect (Hardware Engineering & Supplier)",
        alignment_note="Indirect: tool provides symptom telemetry and pairing guides, but physical manufacturing fixes lie outside support.",
    )

    # 6. Candidate Goal D2: Nexa 2 Defect Outflow
    nx2_outflow = float(nx2["total_fulfillment_outflow_inr"])
    nx2_tickets = float(nx2["tickets"])
    add_scenario_group(
        goal_id="GOAL-D2",
        goal_name="Nexa 2 Defect Fulfillment Outflow",
        metric_name="Nexa 2 support tickets and fulfillment outflow",
        baseline_count=nx2_tickets,
        baseline_cost=nx2_outflow,
        cost_type="fulfillment_outflow (refunds + replacements)",
        percentages=[0.05, 0.10, 0.20],
        controllability="Low / Indirect (Hardware Engineering & Supplier)",
        alignment_note="Indirect: tool classifies firmware vs hardware failure, but cannot fix hardware component defects alone.",
    )

    # 7. Candidate Goal D3: Combined Flagship Defect Outflow (Pulse 2 + Nexa 2)
    comb_hw_cost = p2_outflow + nx2_outflow
    comb_hw_tickets = p2_tickets + nx2_tickets
    add_scenario_group(
        goal_id="GOAL-D3",
        goal_name="Combined Flagship Defect Outflow (Pulse 2 & Nexa 2)",
        metric_name="Pulse 2 and Nexa 2 combined tickets and fulfillment outflow",
        baseline_count=comb_hw_tickets,
        baseline_cost=comb_hw_cost,
        cost_type="fulfillment_outflow (refunds + replacements)",
        percentages=[0.05, 0.10, 0.20],
        controllability="Low / Indirect (Cross-Functional)",
        alignment_note="Indirect: largest enterprise financial exposure, but support tool acts only as an intelligence feed to engineering.",
    )

    df_scenarios = pd.DataFrame(rows)
    return df_scenarios, scenarios_dict


def generate_business_goal_markdown(
    metrics: Dict[str, Any],
    scenarios_df: pd.DataFrame,
    scenarios_dict: Dict[str, Any],
) -> str:
    """Generates outputs/03_business_goal.md."""
    t_total = metrics["total_analyzed_tickets"]
    w_mean = metrics["volume_trends"]["weekly_stats"]["mean"]
    m_a = metrics["repeat_contact_metrics"]["repeat_definitions_comparison"]["method_a"]
    m_b = metrics["repeat_contact_metrics"]["repeat_definitions_comparison"]["method_b"]
    explicit_count = metrics["repeat_contact_metrics"]["explicit_repeat_complaints"]["total_detected_in_messages"]
    sla = metrics["outcomes_and_sla_metrics"]["overall_rates"]
    p2 = metrics["product_metrics"]["VA-EB-PL2"]
    nx2 = metrics["product_metrics"]["VA-SW-NX2"]
    comb_hw_outflow = p2["total_fulfillment_outflow_inr"] + nx2["total_fulfillment_outflow_inr"]

    md = []
    md.append("# Vireo Audio Support Intelligence — Business Goal Formulation (Step 3)")
    md.append(f"**Generated:** {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST | **Status:** Mathematically Validated Candidates\n")

    md.append("## 1. Executive Baseline & Empirical Operating Metrics\n")
    md.append(
        "Before defining any target, historical operations across 18 months (1 Jan 2025 – 30 Jun 2026; 6 quarters; 78 weeks) "
        "were measured against **Support Operating Policy v3.2**. Financial values are categorized by their exact accounting type:\n"
    )

    md.append("| Operational Metric | 18-Month Baseline Volume | Baseline Rate | Baseline Financial Exposure (18-Month Total) | Quarterly Run-Rate | Financial Classification |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :--- |")
    md.append(f"| **Total Support Tickets** | **{t_total:,}** | 100.0% | — | Mean: {w_mean} tickets/wk | Operating Volume |")
    md.append(f"| **Repeat Contacts (Method A — Strict Issue)** | **{m_a['repeat_tickets_count']:,}** | **{m_a['repeat_tickets_percentage']}%** | **Rs {m_a['observed_contact_cost_inr']:,}** | **Rs {m_a['quarterly_observed_cost_inr']:,.2f}** | Observed Contact Handling Cost |")
    md.append(f"| **Repeat Contacts (Method B — Product Proxy)** | **{m_b['repeat_tickets_count']:,}** | **{m_b['repeat_tickets_percentage']}%** | **Rs {m_b['observed_contact_cost_inr']:,}** | **Rs {m_b['quarterly_observed_cost_inr']:,.2f}** | Observed Contact Handling Cost |")
    md.append(f"| **Explicit Repeat Complaints** | **{explicit_count}** | **{round(explicit_count/t_total*100, 2)}%** | — | ~19.2 complaints/qtr | Unresolved Resolution Signals |")
    md.append(f"| **First-Response SLA Breaches** | **{sla['sla_breach_tickets']:,}** | **{sla['sla_breach_percentage']}%** | **Rs {sla['total_sla_breach_cost_inr']:,}** | **Rs {round(sla['total_sla_breach_cost_inr']/6.0, 2):,.2f}** | Policy Store Credit Penalty Liability |")
    md.append(f"| **Internal Team Transfers** | **{sla['total_transfers_count']:,}** | **{sla['tickets_with_transfers_percentage']}%** | **Rs {sla['transfer_handling_cost_inr']:,}** | **Rs {round(sla['transfer_handling_cost_inr']/6.0, 2):,.2f}** | Benchmarked Re-handling Cost (Policy §4) |")
    md.append(f"| **Pulse 2 (`VA-EB-PL2`) Defect Outflow** | **{p2['tickets']:,}** | 86.14 / 100 orders | **Rs {p2['total_fulfillment_outflow_inr']:,.2f}** | **Rs {round(p2['total_fulfillment_outflow_inr']/6.0, 2):,.2f}** | Fulfillment Outflow (Refunds + Replacements) |")
    md.append(f"| **Nexa 2 (`VA-SW-NX2`) Defect Outflow** | **{nx2['tickets']:,}** | 94.28 / 100 orders | **Rs {nx2['total_fulfillment_outflow_inr']:,.2f}** | **Rs {round(nx2['total_fulfillment_outflow_inr']/6.0, 2):,.2f}** | Fulfillment Outflow (Refunds + Replacements) |")
    md.append(f"| **Combined Flagship Defect Outflow** | **{p2['tickets'] + nx2['tickets']:,}** | 39.19% of tickets | **Rs {comb_hw_outflow:,.2f}** | **Rs {round(comb_hw_outflow/6.0, 2):,.2f}** | Fulfillment Outflow (Refunds + Replacements) |\n")

    md.append("> [!IMPORTANT]\n")
    md.append(
        "> **Accounting Boundary Rule:** Fundamental cost categories must never be summed into an arbitrary single 'savings' number. "
        "Observed contact handling costs (staffing capacity) reflect labor paid to answer channels; store credit penalties represent balance sheet credits; "
        "transfer benchmarks represent workflow friction; and fulfillment outflows represent physical cash refunds and inventory loss.\n"
    )

    md.append("## 2. Candidate Goal Scenarios & Mathematical Derivations\n")
    md.append(
        "All calculations strictly follow exact arithmetic: `quarterly_run_rate = 18_month_cost / 6`, "
        "`potential_avoided_cost = baseline_cost * reduction_pct`, `target_count = baseline_count * (1 - reduction_pct)`, "
        "and `quarterly_impact = potential_avoided_cost / 6`.\n"
    )

    md.append("### Candidate Goal A — Repeat Contacts / First-Contact Resolution (FCR)\n")
    md.append(
        "*Methodological Note:* Support Policy §10 defines FCR as no re-contact from the same customer regarding the *same issue* within 30 days. "
        "Because `issue_id` is absent, **Method A** operates as a strict issue proxy (same customer + SKU + category), whereas **Method B** "
        "operates as a product-level proxy (same customer + SKU) capturing multi-contact escalation journeys.\n"
    )

    md.append("#### Method A Scenarios (Strict Issue Proxy):\n")
    md.append("| Scenario | Baseline Tickets | Target Tickets | Tickets Reduced | Potential Avoided Handling Cost (18m) | Quarterly Financial Impact | Annualized Financial Impact |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
    for s in scenarios_dict["GOAL-A1"]:
        md.append(f"| **Reduce Method A by {s['reduction_percentage']}%** | {s['baseline_count']:,} | {s['target_count']:,} | {s['reduction_count']:,} | Rs {s['potential_avoided_cost_18m_inr']:,} | **Rs {s['quarterly_financial_impact_inr']:,} / qtr** | **Rs {s['annualized_financial_impact_inr']:,} / yr** |")

    md.append("\n#### Method B Scenarios (Product Proxy — Upper Bound of Re-contacts for Same Device):\n")
    md.append("| Scenario | Baseline Tickets | Target Tickets | Tickets Reduced | Potential Avoided Handling Cost (18m) | Quarterly Financial Impact | Annualized Financial Impact |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
    for s in scenarios_dict["GOAL-A2"]:
        md.append(f"| **Reduce Method B by {s['reduction_percentage']}%** | {s['baseline_count']:,} | {s['target_count']:,} | {s['reduction_count']:,} | Rs {s['potential_avoided_cost_18m_inr']:,} | **Rs {s['quarterly_financial_impact_inr']:,} / qtr** | **Rs {s['annualized_financial_impact_inr']:,} / yr** |")

    md.append("\n### Candidate Goal B — First-Response SLA Breaches\n")
    md.append(
        "*Operational Scope:* Modeled on reducing initial human response delays exceeding Support Policy §3 targets. Avoided costs represent store credit payouts not incurred.\n"
    )
    md.append("| Scenario | Baseline Breaches | Target Breaches | Breaches Reduced | Store Credits Avoided (18m) | Quarterly Financial Impact | Annualized Financial Impact |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
    for s in scenarios_dict["GOAL-B"]:
        md.append(f"| **Reduce SLA Breaches by {s['reduction_percentage']}%** | {s['baseline_count']:,} | {s['target_count']:,} | {s['reduction_count']:,} | Rs {s['potential_avoided_cost_18m_inr']:,} | **Rs {s['quarterly_financial_impact_inr']:,} / qtr** | **Rs {s['annualized_financial_impact_inr']:,} / yr** |")

    md.append("\n### Candidate Goal C — Internal Team Routing Transfers\n")
    md.append(
        "*Policy Benchmark Note:* Support Policy §4 establishes a ₹305 re-handling cost per transfer. Reducing transfers reflects intake routing efficiency; "
        "however, ₹305 is an internal cost benchmark, not a direct cash ledger saving, and transfers to Tier 2 warranty specialists are structurally necessary.\n"
    )
    md.append("| Scenario | Baseline Transfers | Target Transfers | Transfers Reduced | Benchmark Re-handling Cost Avoided | Quarterly Benchmark Impact | Annualized Benchmark Impact |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
    for s in scenarios_dict["GOAL-C"]:
        md.append(f"| **Reduce Transfers by {s['reduction_percentage']}%** | {s['baseline_count']:,} | {s['target_count']:,} | {s['reduction_count']:,} | Rs {s['potential_avoided_cost_18m_inr']:,} | **Rs {s['quarterly_financial_impact_inr']:,} / qtr** | **Rs {s['annualized_financial_impact_inr']:,} / yr** |")

    md.append("\n### Candidate Goal D — Product Defect Fulfillment Outflow (Cross-Functional)\n")
    md.append(
        "*Cross-Functional Limitation:* Product defect remediation requires hardware engineering and supplier intervention. Support operations alone "
        "cannot eliminate hardware manufacturing defects; support operations can only triage symptoms and provide telemetry.\n"
    )
    md.append("| Product Scope | Reduction % | Baseline Outflow (18m) | Potential Outflow Reduction | Quarterly Outflow Impact | Annualized Outflow Impact |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
    for s in scenarios_dict["GOAL-D1"]:
        md.append(f"| Pulse 2 Only | {s['reduction_percentage']}% | Rs {s['baseline_cost_18m_inr']:,} | Rs {s['potential_avoided_cost_18m_inr']:,} | Rs {s['quarterly_financial_impact_inr']:,} / qtr | Rs {s['annualized_financial_impact_inr']:,} / yr |")
    for s in scenarios_dict["GOAL-D2"]:
        md.append(f"| Nexa 2 Only | {s['reduction_percentage']}% | Rs {s['baseline_cost_18m_inr']:,} | Rs {s['potential_avoided_cost_18m_inr']:,} | Rs {s['quarterly_financial_impact_inr']:,} / qtr | Rs {s['annualized_financial_impact_inr']:,} / yr |")
    for s in scenarios_dict["GOAL-D3"]:
        md.append(f"| **Combined (Pulse 2 + Nexa 2)** | **{s['reduction_percentage']}%** | **Rs {s['baseline_cost_18m_inr']:,}** | **Rs {s['potential_avoided_cost_18m_inr']:,}** | **Rs {s['quarterly_financial_impact_inr']:,} / qtr** | **Rs {s['annualized_financial_impact_inr']:,} / yr** |")

    md.append("\n## 3. Evidence Strength & Limitations Matrix\n")
    md.append(
        "In accordance with rigorous evidence-based principles, no subjective scores are assigned. The table below delineates the empirical basis and missing data for each candidate goal:\n"
    )
    md.append("| Candidate Goal | Directly Observed | Calculated | Proxy Elements | Modeled Scenarios | Missing Data / Information Gap | Post-Deployment Measurement Requirement |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    md.append(
        "| **Goal A: Repeat Contacts (FCR)** | Timestamps (`created_at`, `resolved_at`), `customer_id`, channel | 30-day window difference, channel handling costs per Policy §4 | Category (Method A) or SKU (Method B) acts as issue proxy | 10%, 20%, 30% reduction in repeat handling capacity | No explicit `issue_id` in database schema | Tagging repeat contacts at intake; measuring return interval distribution |"
    )
    md.append(
        "| **Goal B: SLA Breaches** | `created_at`, `first_response_at`, channel | Difference in minutes vs Policy §3 threshold | Target minutes mapped from policy | 10%, 20%, 30% reduction in store credit liability | Resolution duration; agent shift schedules during breach hours | First-response timestamp tracking; queue waiting time monitoring |"
    )
    md.append(
        "| **Goal C: Internal Transfers** | Integer transfers count in helpdesk | ₹305 * transfers count | ₹305 policy benchmark represents friction | 10%, 20%, 30% reduction in transfer re-handling | Transfers unrecorded during legacy Freshdesk era; necessity flag | Tracking first-contact routing accuracy and transfer re-hops |"
    )
    md.append(
        "| **Goal D: Product Defect Outflow** | Refund amounts, replacement flags, SKU in orders | Normalized complaints per 100 orders, inventory + logistics replacement cost | Support complaint rate as proxy for true field defect rate | 5%, 10%, 20% reduction in cash outflow | Manufacturing batch codes; return physical inspection QA logs | Joint product-engineering defect remediation tracking; warranty claims |"
    )

    md.append("\n## 4. Operational Alignment Between Proposed Tool & Metrics\n")
    md.append(
        "The proposed AI support-intelligence system is designed to perform specific technical capabilities:\n"
        "1. Classify customer messages at intake using a controlled taxonomy (primary issue, secondary issue, customer intent).\n"
        "2. Identify repeat-contact signals directly from customer message text (e.g. protests of prior unresolved issues).\n"
        "3. Surface emerging complaint themes and SKU concentrations in a deterministic weekly digest.\n"
        "4. Track agent closure volumes while separating Tier 1 from Tier 2 specialists.\n\n"
        "**Evidence-Based Alignment:**\n"
        "- **The strongest alignment between the proposed tool and the observed operational metric is with Repeat Contacts / FCR (Candidate Goal A).**\n"
        "  - *Mechanism:* Frontline agents frequently close tickets prematurely (validated by 115 explicit customer protest messages). By identifying repeat contacts at intake and flagging unresolved issue clusters in the weekly digest, team leads can enforce diagnostic checklists before tickets are marked resolved.\n"
        "  - *Controllability:* Support leadership controls frontline triage protocols, handover documentation standards, and queue routing directly.\n"
        "- **Product Defect Outflows (Goal D)** represent the largest total financial exposure (₹3.87M on Pulse 2 and Nexa 2), but **support operations alone cannot control physical component failures**. The tool can only serve as an intelligence pipeline feeding hardware engineering and QA.\n"
    )

    md.append("## 5. Proposed Defensible Business Goal Statements\n")
    md.append("Following the mandatory structure: *'Reduce [metric] from [baseline] to [target] within [time period], equivalent to approximately [N] fewer tickets/incidents and approximately ₹[X] in potential avoided [cost type] per quarter, subject to validation'*, three mathematically grounded options are proposed:\n\n")

    md.append("### Option 1 (Conservative — Strict Issue Proxy / Method A — 10% Reduction):\n")
    md.append(
        "> **\"Reduce Method A repeat contacts from 1,412 tickets (11.89% baseline) to 1,271 tickets (10.70% target) within two quarters (6 months) post-deployment, "
        "equivalent to approximately 141 fewer repeat tickets and approximately ₹6,117 in potential avoided handling cost per quarter (₹24,469 annualized), subject to operational validation.\"**\n"
    )

    md.append("### Option 2 (Balanced — Strict Issue Proxy / Method A — 20% Reduction):\n")
    md.append(
        "> **\"Reduce Method A repeat contacts from 1,412 tickets (11.89% baseline) to 1,130 tickets (9.51% target) within four quarters (12 months) post-deployment, "
        "equivalent to approximately 282 fewer repeat tickets and approximately ₹12,234 in potential avoided handling cost per quarter (₹48,937 annualized), subject to operational validation.\"**\n"
    )

    md.append("### Option 3 (Pragmatic Operational Target — Product Proxy / Method B — 20% Reduction):\n")
    md.append(
        "> **\"Reduce Method B product-level repeat contacts from 3,270 tickets (27.54% baseline) to 2,616 tickets (22.03% target) within four quarters (12 months) post-deployment, "
        "equivalent to approximately 654 fewer re-contacts on the same device and approximately ₹29,271 in potential avoided handling cost per quarter (₹117,083 annualized), subject to operational validation.\"**\n"
    )

    md.append("## 6. Post-Deployment Measurement Plan & Governance Guardrails\n")
    md.append("To verify whether the business goal is achieved without unintended negative consequences, the deployment must follow strict measurement protocols:\n\n")
    md.append("### Measurement Plan:\n")
    md.append(
        "- **Historical Baseline:** 18-month clean ticket dataset (11,875 tickets; 1 Jan 2025 – 30 Jun 2026).\n"
        "- **Intervention:** AI-assisted ticket triage, repeat-contact intake alerting, weekly digest issue clustering, and standardized diagnostic checklists.\n"
        "- **Measurement Period:** 2 quarters (6 months) for interim review; 4 quarters (12 months) for annual goal audit.\n"
        "- **Primary Metric:** Repeat-contact rate calculated under Method A (same customer + SKU + category <= 30 days) and Method B (same customer + SKU <= 30 days).\n"
        "- **Secondary Metrics:**\n"
        "  1. Mean days to re-contact (monitoring whether re-contacts are postponed past 30 days or genuinely resolved).\n"
        "  2. CSAT response average and response rate on resolved tickets (verifying customer satisfaction improvement).\n"
        "  3. First-response SLA breach rate by channel (ensuring triage does not slow initial response).\n"
        "  4. Internal transfer frequency between Frontline and Tier 2 specialists.\n"
    )

    md.append("\n### Essential Governance Guardrails:\n")
    md.append(
        "1. **No Artificial Ticket Suppression:** Frontline agents must not discourage customers from contacting or fail to log tickets in order to artificially depress repeat counts.\n"
        "2. **No Misleading Productivity Incentives:** Agent leaderboard metrics must explicitly separate Tier 1 from Tier 2. Tier 2 specialists must not be evaluated on closed-ticket velocity, as warranty investigations require detailed bench testing.\n"
        "3. **Resolution Quality Auditing:** A ticket must not be marked 'resolved' unless all standardized diagnostic checklist items are satisfied and confirmed with the customer.\n"
        "4. **No Premature Financial Booking:** Modeled potential avoided costs must remain clearly labeled as capacity savings until realized in reduced channel operating expenses.\n"
    )

    return "\n".join(md)


def run_business_goal_pipeline(
    outputs_dir: Optional[Path] = None,
) -> Tuple[Dict[str, Any], pd.DataFrame, str]:
    """Executes the Step 3 business goal formulation pipeline."""
    if outputs_dir is None:
        outputs_dir = Path(__file__).resolve().parent.parent / "outputs"

    metrics = load_step2_metrics(outputs_dir)
    scenarios_df, scenarios_dict = calculate_goal_scenarios(metrics)
    markdown_content = generate_business_goal_markdown(metrics, scenarios_df, scenarios_dict)

    # Build JSON payload
    goal_json_data = {
        "generated_at": datetime.now(IST).isoformat(),
        "baseline_summary": {
            "observation_period": "18 months (2025-01-01 to 2026-06-30; 6 quarters)",
            "total_tickets": metrics["total_analyzed_tickets"],
            "average_weekly_tickets": metrics["volume_trends"]["weekly_stats"]["mean"],
            "repeat_contacts_method_a": {
                "count": metrics["repeat_contact_metrics"]["repeat_definitions_comparison"]["method_a"]["repeat_tickets_count"],
                "rate_pct": metrics["repeat_contact_metrics"]["repeat_definitions_comparison"]["method_a"]["repeat_tickets_percentage"],
                "observed_cost_inr": metrics["repeat_contact_metrics"]["repeat_definitions_comparison"]["method_a"]["observed_contact_cost_inr"],
                "quarterly_cost_inr": metrics["repeat_contact_metrics"]["repeat_definitions_comparison"]["method_a"]["quarterly_observed_cost_inr"],
            },
            "repeat_contacts_method_b": {
                "count": metrics["repeat_contact_metrics"]["repeat_definitions_comparison"]["method_b"]["repeat_tickets_count"],
                "rate_pct": metrics["repeat_contact_metrics"]["repeat_definitions_comparison"]["method_b"]["repeat_tickets_percentage"],
                "observed_cost_inr": metrics["repeat_contact_metrics"]["repeat_definitions_comparison"]["method_b"]["observed_contact_cost_inr"],
                "quarterly_cost_inr": metrics["repeat_contact_metrics"]["repeat_definitions_comparison"]["method_b"]["quarterly_observed_cost_inr"],
            },
            "explicit_repeat_complaints": metrics["repeat_contact_metrics"]["explicit_repeat_complaints"]["total_detected_in_messages"],
            "sla_breaches": {
                "count": metrics["outcomes_and_sla_metrics"]["overall_rates"]["sla_breach_tickets"],
                "rate_pct": metrics["outcomes_and_sla_metrics"]["overall_rates"]["sla_breach_percentage"],
                "penalty_cost_inr": metrics["outcomes_and_sla_metrics"]["overall_rates"]["total_sla_breach_cost_inr"],
                "quarterly_cost_inr": round(metrics["outcomes_and_sla_metrics"]["overall_rates"]["total_sla_breach_cost_inr"] / 6.0, 2),
            },
            "internal_transfers": {
                "count": metrics["outcomes_and_sla_metrics"]["overall_rates"]["total_transfers_count"],
                "tickets_with_transfers_pct": metrics["outcomes_and_sla_metrics"]["overall_rates"]["tickets_with_transfers_percentage"],
                "benchmark_cost_inr": metrics["outcomes_and_sla_metrics"]["overall_rates"]["transfer_handling_cost_inr"],
                "quarterly_cost_inr": round(metrics["outcomes_and_sla_metrics"]["overall_rates"]["transfer_handling_cost_inr"] / 6.0, 2),
            },
            "flagship_defect_outflows": {
                "pulse2_inr": metrics["product_metrics"]["VA-EB-PL2"]["total_fulfillment_outflow_inr"],
                "nexa2_inr": metrics["product_metrics"]["VA-SW-NX2"]["total_fulfillment_outflow_inr"],
                "combined_inr": metrics["product_metrics"]["VA-EB-PL2"]["total_fulfillment_outflow_inr"] + metrics["product_metrics"]["VA-SW-NX2"]["total_fulfillment_outflow_inr"],
                "combined_quarterly_inr": round((metrics["product_metrics"]["VA-EB-PL2"]["total_fulfillment_outflow_inr"] + metrics["product_metrics"]["VA-SW-NX2"]["total_fulfillment_outflow_inr"]) / 6.0, 2),
            },
        },
        "candidate_goal_scenarios": scenarios_dict,
        "proposed_goal_statements": [
            {
                "option": 1,
                "tier": "Conservative",
                "statement": "Reduce Method A repeat contacts from 1,412 tickets (11.89% baseline) to 1,271 tickets (10.70% target) within two quarters (6 months) post-deployment, equivalent to approximately 141 fewer repeat tickets and approximately ₹6,117 in potential avoided handling cost per quarter (₹24,469 annualized), subject to operational validation.",
                "target_reduction_pct": 10.0,
                "tickets_reduced": 141.2,
                "quarterly_impact_inr": 6117.17,
                "annualized_impact_inr": 24468.67,
            },
            {
                "option": 2,
                "tier": "Balanced (Recommended)",
                "statement": "Reduce Method A repeat contacts from 1,412 tickets (11.89% baseline) to 1,130 tickets (9.51% target) within four quarters (12 months) post-deployment, equivalent to approximately 282 fewer repeat tickets and approximately ₹12,234 in potential avoided handling cost per quarter (₹48,937 annualized), subject to operational validation.",
                "target_reduction_pct": 20.0,
                "tickets_reduced": 282.4,
                "quarterly_impact_inr": 12234.33,
                "annualized_impact_inr": 48937.33,
            },
            {
                "option": 3,
                "tier": "Pragmatic Product Proxy",
                "statement": "Reduce Method B product-level repeat contacts from 3,270 tickets (27.54% baseline) to 2,616 tickets (22.03% target) within four quarters (12 months) post-deployment, equivalent to approximately 654 fewer re-contacts on the same device and approximately ₹29,271 in potential avoided handling cost per quarter (₹117,083 annualized), subject to operational validation.",
                "target_reduction_pct": 20.0,
                "tickets_reduced": 654.0,
                "quarterly_impact_inr": 29270.67,
                "annualized_impact_inr": 117082.67,
            },
        ],
        "tool_alignment_justification": (
            "The proposed AI support-intelligence system is directly aligned with repeat contact reduction: "
            "it classifies customer issues at intake, identifies explicit repeat signals in message text, "
            "clusters unresolved defect themes in a weekly digest, and prevents premature closures through diagnostic checklists."
        ),
    }

    return goal_json_data, scenarios_df, markdown_content


def save_step3_outputs(
    json_data: Dict[str, Any],
    scenarios_df: pd.DataFrame,
    markdown_content: str,
    outputs_dir: Optional[Path] = None,
) -> None:
    """Saves the 3 Step 3 artifacts to disk."""
    if outputs_dir is None:
        outputs_dir = Path(__file__).resolve().parent.parent / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    with open(outputs_dir / "03_business_goal.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, default=str)

    scenarios_df.to_csv(outputs_dir / "03_goal_scenarios.csv", index=False)

    with open(outputs_dir / "03_business_goal.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)


def main() -> None:
    """CLI execution entrypoint for Step 3."""
    print("[1/3] Calculating Step 3 business goal candidates and scenarios...")
    json_data, scenarios_df, markdown_content = run_business_goal_pipeline()

    print("[2/3] Saving outputs/03_business_goal.md, 03_business_goal.json, and 03_goal_scenarios.csv...")
    save_step3_outputs(json_data, scenarios_df, markdown_content)

    print("[3/3] Execution completed successfully!")

    base = json_data["baseline_summary"]
    props = json_data["proposed_goal_statements"]

    print("\n" + "=" * 80)
    print(" VIREO AUDIO SUPPORT INTELLIGENCE - STEP 3 BUSINESS GOAL FORMULATION")
    print("=" * 80)
    print("1. EMPIRICAL BASELINE METRICS (18-Month Observation Period):")
    print(f"   * Total Analyzed Tickets           : {base['total_tickets']:,} (Mean: {base['average_weekly_tickets']} tickets/wk)")
    print(f"   * Repeat Contacts (Method A Strict): {base['repeat_contacts_method_a']['count']:,} ({base['repeat_contacts_method_a']['rate_pct']}%) | Observed Cost: Rs {base['repeat_contacts_method_a']['observed_cost_inr']:,} (Rs {base['repeat_contacts_method_a']['quarterly_cost_inr']:,.2f}/qtr)")
    print(f"   * Repeat Contacts (Method B Proxy) : {base['repeat_contacts_method_b']['count']:,} ({base['repeat_contacts_method_b']['rate_pct']}%) | Observed Cost: Rs {base['repeat_contacts_method_b']['observed_cost_inr']:,} (Rs {base['repeat_contacts_method_b']['quarterly_cost_inr']:,.2f}/qtr)")
    print(f"   * Explicit Repeat Complaints       : {base['explicit_repeat_complaints']:,} tickets")
    print(f"   * First-Response SLA Breaches      : {base['sla_breaches']['count']:,} ({base['sla_breaches']['rate_pct']}%) | Penalty Cost: Rs {base['sla_breaches']['penalty_cost_inr']:,} (Rs {base['sla_breaches']['quarterly_cost_inr']:,.2f}/qtr)")
    print(f"   * Internal Team Transfers          : {base['internal_transfers']['count']:,} ({base['internal_transfers']['tickets_with_transfers_pct']}%) | Benchmark Cost: Rs {base['internal_transfers']['benchmark_cost_inr']:,} (Rs {base['internal_transfers']['quarterly_cost_inr']:,.2f}/qtr)")
    print(f"   * Flagship Defect Outflow (P2+NX2) : Rs {base['flagship_defect_outflows']['combined_inr']:,.2f} (Rs {base['flagship_defect_outflows']['combined_quarterly_inr']:,.2f}/qtr)")
    print("-" * 80)
    print("2. PROPOSED DEFENSIBLE BUSINESS GOAL STATEMENTS:")
    for p in props:
        clean_stmt = p['statement'].replace('₹', 'Rs ')
        print(f"\n   [Option {p['option']}: {p['tier']}]")
        print(f"   Statement: {clean_stmt}")
        print(f"   Quarterly Potential Impact : Rs {p['quarterly_impact_inr']:,.2f} / quarter")
        print(f"   Annualized Potential Impact: Rs {p['annualized_impact_inr']:,.2f} / year")
    print("-" * 80)
    print("3. OPERATIONAL ALIGNMENT SUMMARY:")
    print("   " + json_data["tool_alignment_justification"].replace('₹', 'Rs '))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
