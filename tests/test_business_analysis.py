"""Unit and Integration Tests for scripts/02_business_analysis.py
Tests business metrics, SLA calculations, repeat contact algorithms, and financial evaluations.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

repo_root = Path(__file__).resolve().parent.parent
script_path = repo_root / "scripts" / "02_business_analysis.py"

spec = importlib.util.spec_from_file_location("business_analysis_mod", script_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["business_analysis_mod"] = mod
spec.loader.exec_module(mod)

calculate_volume_trends = mod.calculate_volume_trends
calculate_category_trends = mod.calculate_category_trends
calculate_product_complaint_rates = mod.calculate_product_complaint_rates
calculate_outcomes_and_sla = mod.calculate_outcomes_and_sla
detect_repeat_contacts = mod.detect_repeat_contacts
evaluate_repeat_contacts = mod.evaluate_repeat_contacts
rank_candidate_business_problems = mod.rank_candidate_business_problems
run_business_analysis = mod.run_business_analysis


@pytest.fixture
def mock_tickets():
    return pd.DataFrame(
        {
            "ticket_id": ["TK-1", "TK-2", "TK-3", "TK-4"],
            "created_at": [
                "2025-01-01 10:00",
                "2025-01-10 12:00",
                "2025-02-15 14:00",
                "2025-01-02 10:00",
            ],
            "created_at_dt": pd.to_datetime([
                "2025-01-01 10:00",
                "2025-01-10 12:00",
                "2025-02-15 14:00",
                "2025-01-02 10:00",
            ]),
            "first_response_at_dt": pd.to_datetime([
                "2025-01-01 10:20",  # chat: 20m > 15m target (Breach)
                "2025-01-10 12:10",  # chat: 10m <= 15m target (OK)
                "2025-02-15 23:00",  # email: 9h > 8h target (Breach)
                "2025-01-02 11:00",  # voice: 1h <= 2h target (OK)
            ]),
            "resolved_at": [
                "2025-01-01 15:00",
                "2025-01-10 16:00",
                "2025-02-15 23:30",
                "2025-01-02 12:00",
            ],
            "resolved_at_dt": pd.to_datetime([
                "2025-01-01 15:00",
                "2025-01-10 16:00",
                "2025-02-15 23:30",
                "2025-01-02 12:00",
            ]),
            "status": ["resolved", "resolved", "resolved", "resolved"],
            "channel": ["chat", "chat", "email", "voice"],
            "customer_id": ["C1", "C1", "C1", "C2"],
            "order_id": ["O1", "O1", "O1", "O2"],
            "product_sku": ["SKU-A", "SKU-A", "SKU-A", "SKU-B"],
            "category": ["Connectivity", "Connectivity", "Returns & Refunds", "Audio Quality"],
            "priority": ["Normal", "Normal", "High", "Low"],
            "assigned_team": ["Chat Frontline", "Chat Frontline", "Returns Desk", "Voice Frontline"],
            "resolving_team": ["Chat Frontline", "Chat Frontline", "Returns Desk", "Voice Frontline"],
            "agent_id": ["A1", "A1", "A2", "A3"],
            "transfers": [0, 1, 0, 0],
            "csat_score": [5.0, 4.0, 3.0, 5.0],
            "refund_amount_inr": [np.nan, np.nan, 2500.0, np.nan],
            "refund_reason_code": [np.nan, np.nan, "RETURN-QC-OK", np.nan],
            "replacement_issued": ["N", "Y", "N", "N"],
            "customer_message": [
                "Bluetooth not connecting",
                "raised this 9 days ago and was told it was resolved",
                "Want refund",
                "Audio distortion",
            ],
            "agent_notes": ["Troubleshot", "Replaced", "Refunded", "Walked through reset"],
            "source_system": ["helpdesk", "helpdesk", "helpdesk", "helpdesk"],
        }
    )


def test_calculate_volume_trends(mock_tickets):
    """Verify weekly and monthly volume aggregation."""
    res = calculate_volume_trends(mock_tickets)
    assert "monthly_volume" in res
    assert "weekly_volume" in res
    assert res["monthly_stats"]["total_months"] == 2
    assert res["monthly_volume"]["2025-01"] == 3
    assert res["monthly_volume"]["2025-02"] == 1


def test_calculate_category_trends(mock_tickets):
    """Verify category distribution and percentage calculation."""
    res = calculate_category_trends(mock_tickets)
    cat_summary = res["overall_categories"]
    assert cat_summary["Connectivity"]["count"] == 2
    assert cat_summary["Connectivity"]["percentage"] == 50.0
    assert cat_summary["Returns & Refunds"]["count"] == 1


def test_calculate_product_complaint_rates(mock_tickets):
    """Verify normalized product complaint rates."""
    orders = pd.DataFrame(
        {
            "order_id": ["O1", "O2", "O3"],
            "sku": ["SKU-A", "SKU-B", "SKU-A"],
            "qty": [1, 2, 1],
        }
    )
    products = pd.DataFrame(
        {
            "sku": ["SKU-A", "SKU-B"],
            "product_name": ["Prod A", "Prod B"],
            "family": ["earbuds", "speaker"],
            "unit_cost_inr": [1000, 2000],
            "retail_price_inr": [2500, 4500],
        }
    )
    rates = calculate_product_complaint_rates(mock_tickets, orders, products)
    assert rates["SKU-A"]["tickets"] == 3
    assert rates["SKU-A"]["orders"] == 2
    assert rates["SKU-A"]["tickets_per_100_orders"] == 150.0  # 3 tickets on 2 orders
    assert rates["SKU-B"]["tickets"] == 1
    assert rates["SKU-B"]["orders"] == 1
    assert rates["SKU-B"]["tickets_per_100_orders"] == 100.0


def test_calculate_outcomes_and_sla(mock_tickets):
    """Verify outcome rates and channel SLA breach calculations."""
    res = calculate_outcomes_and_sla(mock_tickets)
    overall = res["overall_rates"]
    assert overall["refund_tickets"] == 1
    assert overall["refund_percentage"] == 25.0
    assert overall["replacement_tickets"] == 1
    assert overall["total_refund_amount_inr"] == 2500.0
    assert overall["total_transfers_count"] == 1
    assert overall["transfer_handling_cost_inr"] == 305  # 1 * 305

    # SLA checks:
    # TK-1: chat 20m > 15m (Breach)
    # TK-2: chat 10m <= 15m (OK)
    # TK-3: email 9h > 8h (Breach)
    # TK-4: voice 1h <= 2h (OK)
    # Total breaches = 2
    assert overall["sla_breach_tickets"] == 2
    assert overall["sla_breach_percentage"] == 50.0
    assert overall["total_sla_breach_cost_inr"] == 700  # 2 * 350

    channel_sla = res["channel_sla_performance"]
    assert channel_sla["chat"]["breaches"] == 1
    assert channel_sla["chat"]["total_tickets"] == 2
    assert channel_sla["email"]["breaches"] == 1
    assert channel_sla["voice"]["breaches"] == 0


def test_detect_repeat_contacts(mock_tickets):
    """Verify 30-day window repeat detection logic."""
    # Method A: customer_id + product_sku
    df_rep = detect_repeat_contacts(mock_tickets, ["customer_id", "product_sku"])
    # TK-1: C1, SKU-A, res=2025-01-01 15:00
    # TK-2: C1, SKU-A, created=2025-01-10 12:00 -> 8.88 days diff <= 30 -> Repeat!
    # TK-3: C1, SKU-A, created=2025-02-15 14:00 -> from TK-2 res (2025-01-10 16:00) is 35.9 days > 30 -> Not Repeat!
    # TK-4: C2, SKU-B -> First contact -> Not Repeat!
    rep_map = dict(zip(df_rep["ticket_id"], df_rep["is_repeat"]))
    assert rep_map["TK-1"] is False
    assert rep_map["TK-2"] is True
    assert rep_map["TK-3"] is False
    assert rep_map["TK-4"] is False


def test_evaluate_repeat_contacts_methods(mock_tickets):
    """Verify comparison between Method A, Method B, and Method D."""
    results, df_out = evaluate_repeat_contacts(mock_tickets)
    methods = results["repeat_definitions_comparison"]
    assert "method_a" in methods
    assert "method_b" in methods
    assert "method_d" in methods

    # Under Method A: TK-2 is repeat (count=1)
    assert methods["method_a"]["repeat_tickets_count"] == 1
    # Under Method B: TK-2 is same category as TK-1 (count=1)
    assert methods["method_b"]["repeat_tickets_count"] == 1
    # Cost for chat repeat = 210
    assert methods["method_a"]["additional_contact_cost_inr"] == 210

    # Phrase detection: TK-2 contains 'raised this 9 days ago and was told it was resolved'
    assert results["colleague_hypothesis_evaluation"]["tickets_with_explicit_premature_resolution_complaint"] == 1


def test_full_business_analysis_execution():
    """Integration test verifying full business analysis executes cleanly on actual files."""
    metrics_data, repeat_df, md_content = run_business_analysis()
    assert metrics_data is not None
    assert len(repeat_df) == 11875
    assert len(md_content) > 1000
    assert "FACT" in md_content
    assert "ASSUMPTION" in md_content
    assert "HYPOTHESIS" in md_content
    assert len(metrics_data["ranked_candidate_problems"]) >= 5
