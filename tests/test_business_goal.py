"""tests/test_business_goal.py

Unit and integration tests for scripts/03_establish_business_goal.py
Verifies mathematical integrity, scenario calculations, policy definitions,
and schema structure for Step 3 business goal formulation.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

repo_root = Path(__file__).resolve().parent.parent
script_path = repo_root / "scripts" / "03_establish_business_goal.py"

spec = importlib.util.spec_from_file_location("business_goal_mod", script_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

load_step2_metrics = mod.load_step2_metrics
calculate_goal_scenarios = mod.calculate_goal_scenarios
run_business_goal_pipeline = mod.run_business_goal_pipeline


@pytest.fixture
def mock_step2_metrics():
    return {
        "total_analyzed_tickets": 1000,
        "volume_trends": {
            "weekly_stats": {"mean": 50.0},
        },
        "repeat_contact_metrics": {
            "repeat_definitions_comparison": {
                "method_a": {
                    "repeat_tickets_count": 100,
                    "repeat_tickets_percentage": 10.0,
                    "observed_contact_cost_inr": 25000.0,
                    "quarterly_observed_cost_inr": 4166.67,
                },
                "method_b": {
                    "repeat_tickets_count": 250,
                    "repeat_tickets_percentage": 25.0,
                    "observed_contact_cost_inr": 62500.0,
                    "quarterly_observed_cost_inr": 10416.67,
                },
            },
            "explicit_repeat_complaints": {
                "total_detected_in_messages": 15,
            },
        },
        "outcomes_and_sla_metrics": {
            "overall_rates": {
                "sla_breach_tickets": 80,
                "sla_breach_percentage": 8.0,
                "total_sla_breach_cost_inr": 28000.0,
                "total_transfers_count": 90,
                "tickets_with_transfers_percentage": 9.0,
                "transfer_handling_cost_inr": 27450.0,
            }
        },
        "product_metrics": {
            "VA-EB-PL2": {
                "tickets": 300,
                "total_fulfillment_outflow_inr": 150000.0,
            },
            "VA-SW-NX2": {
                "tickets": 100,
                "total_fulfillment_outflow_inr": 100000.0,
            },
        },
    }


def test_scenario_mathematical_identities(mock_step2_metrics):
    """Verifies the core mathematical identities required by Step 3:

    - quarterly_run_rate = 18_month_cost / 6
    - potential_avoided_cost = baseline_cost * reduction_percentage
    - target_count = baseline_count * (1 - reduction_percentage)
    - reduction_count = baseline_count - target_count
    """
    df, scenarios_dict = calculate_goal_scenarios(mock_step2_metrics)

    for _, row in df.iterrows():
        pct = row["reduction_percentage"] / 100.0
        baseline_cnt = row["baseline_count"]
        target_cnt = row["target_count"]
        reduced_cnt = row["reduction_count"]
        baseline_cost = row["baseline_cost_18m_inr"]
        avoided_cost = row["potential_avoided_cost_18m_inr"]
        q_impact = row["quarterly_financial_impact_inr"]
        ann_impact = row["annualized_financial_impact_inr"]

        # 1. target_count = baseline_count * (1 - pct)
        assert np.isclose(target_cnt, baseline_cnt * (1.0 - pct), atol=0.1)

        # 2. reduction_count = baseline_count - target_count
        assert np.isclose(reduced_cnt, baseline_cnt - target_cnt, atol=0.1)

        # 3. potential_avoided_cost = baseline_cost * pct
        assert np.isclose(avoided_cost, baseline_cost * pct, atol=0.5)

        # 4. quarterly_impact = avoided_cost / 6.0
        assert np.isclose(q_impact, avoided_cost / 6.0, atol=0.1)

        # 5. annualized_impact = quarterly_impact * 4.0
        assert np.isclose(ann_impact, q_impact * 4.0, atol=0.1)


def test_repeat_contact_scenarios(mock_step2_metrics):
    """Verifies that Repeat Contact Method A and Method B produce the required 10%, 20%, 30% scenarios."""
    df, scenarios_dict = calculate_goal_scenarios(mock_step2_metrics)

    a1 = scenarios_dict["GOAL-A1"]
    assert len(a1) == 3
    assert a1[0]["reduction_percentage"] == 10.0
    assert a1[0]["reduction_count"] == 10.0
    assert a1[0]["potential_avoided_cost_18m_inr"] == 2500.0

    assert a1[1]["reduction_percentage"] == 20.0
    assert a1[1]["reduction_count"] == 20.0
    assert a1[1]["potential_avoided_cost_18m_inr"] == 5000.0

    assert a1[2]["reduction_percentage"] == 30.0
    assert a1[2]["reduction_count"] == 30.0
    assert a1[2]["potential_avoided_cost_18m_inr"] == 7500.0

    a2 = scenarios_dict["GOAL-A2"]
    assert len(a2) == 3
    assert a2[1]["reduction_percentage"] == 20.0
    assert a2[1]["reduction_count"] == 50.0  # 250 * 0.20
    assert a2[1]["potential_avoided_cost_18m_inr"] == 12500.0  # 62500 * 0.20


def test_sla_and_transfer_scenarios(mock_step2_metrics):
    """Verifies SLA and transfer scenario calculations."""
    df, scenarios_dict = calculate_goal_scenarios(mock_step2_metrics)

    sla_scens = scenarios_dict["GOAL-B"]
    assert len(sla_scens) == 3
    assert sla_scens[1]["reduction_percentage"] == 20.0
    assert sla_scens[1]["reduction_count"] == 16.0  # 80 * 0.20
    assert sla_scens[1]["potential_avoided_cost_18m_inr"] == 5600.0  # 28000 * 0.20

    tr_scens = scenarios_dict["GOAL-C"]
    assert len(tr_scens) == 3
    assert tr_scens[1]["reduction_percentage"] == 20.0
    assert tr_scens[1]["reduction_count"] == 18.0  # 90 * 0.20
    assert tr_scens[1]["potential_avoided_cost_18m_inr"] == 5490.0  # 27450 * 0.20


def test_full_pipeline_execution_and_schema():
    """Integration test running full business goal pipeline on actual output files."""
    json_data, scenarios_df, markdown_content = run_business_goal_pipeline()

    # 1. Baseline verification against actual dataset
    base = json_data["baseline_summary"]
    assert base["total_tickets"] == 11875
    assert base["repeat_contacts_method_a"]["count"] == 1412
    assert base["repeat_contacts_method_a"]["rate_pct"] == 11.89
    assert base["repeat_contacts_method_b"]["count"] == 3270
    assert base["repeat_contacts_method_b"]["rate_pct"] == 27.54
    assert base["explicit_repeat_complaints"] == 115
    assert base["sla_breaches"]["count"] == 1051
    assert base["internal_transfers"]["count"] == 1169
    assert base["flagship_defect_outflows"]["combined_inr"] == 3868220.0

    # 2. DataFrame schema
    expected_cols = [
        "goal_id", "goal_name", "metric_name", "reduction_percentage",
        "baseline_count", "target_count", "reduction_count",
        "baseline_cost_18m_inr", "cost_type", "potential_avoided_cost_18m_inr",
        "quarterly_financial_impact_inr", "annualized_financial_impact_inr",
        "operational_controllability", "tool_alignment"
    ]
    for col in expected_cols:
        assert col in scenarios_df.columns

    # 3. Markdown content assertions
    assert "Executive Baseline & Empirical Operating Metrics" in markdown_content
    assert "Candidate Goal A — Repeat Contacts" in markdown_content
    assert "Candidate Goal B — First-Response SLA Breaches" in markdown_content
    assert "Candidate Goal C — Internal Team Routing Transfers" in markdown_content
    assert "Candidate Goal D — Product Defect Fulfillment Outflow" in markdown_content
    assert "Evidence Strength & Limitations Matrix" in markdown_content
    assert "Proposed Defensible Business Goal Statements" in markdown_content
    assert "Post-Deployment Measurement Plan & Governance Guardrails" in markdown_content

    # 4. Mandatory goal statement structure check
    assert len(json_data["proposed_goal_statements"]) >= 3
    for stmt in json_data["proposed_goal_statements"]:
        s = stmt["statement"]
        assert "Reduce" in s
        assert "from" in s
        assert "to" in s
        assert "within" in s
        assert "potential avoided" in s
        assert "quarter" in s
