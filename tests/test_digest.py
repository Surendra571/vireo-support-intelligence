"""Unit and integration tests for scripts/04_generate_digest.py.
Tests deterministic metrics calculation, week-over-week deltas, partial-week handling,
markdown narrative consistency, and end-to-end pipeline execution.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
import pytest

# Add repo root to path
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import importlib.util

script_path = repo_root / "scripts" / "04_generate_digest.py"
spec = importlib.util.spec_from_file_location("generate_digest_mod", script_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["generate_digest_mod"] = mod
spec.loader.exec_module(mod)

calculate_single_week_metrics = mod.calculate_single_week_metrics
calculate_wow_changes = mod.calculate_wow_changes
build_deterministic_narrative = mod.build_deterministic_narrative
load_and_prepare_digest_data = mod.load_and_prepare_digest_data
run_digest_pipeline = mod.run_digest_pipeline


@pytest.fixture(scope="module")
def prepared_digest_data():
    """Fixture providing loaded and deduplicated data for testing."""
    df, products, orders = load_and_prepare_digest_data()
    return df, products, orders


def test_calculate_single_week_metrics_schema(prepared_digest_data):
    """Verify that weekly metrics dictionary contains all required operational dimensions and proxies."""
    df, products, orders = prepared_digest_data
    week = "2026-W26"
    stats = calculate_single_week_metrics(df, week, products, orders)

    assert stats["week"] == week
    assert stats["total_tickets"] == 199
    assert stats["is_complete_week"] is True
    assert stats["days_covered"] == 7

    # 1. Total & Channel
    assert "channel_breakdown" in stats
    assert set(stats["channel_breakdown"].keys()) == {"chat", "email", "voice", "social"}
    assert stats["channel_breakdown"]["chat"]["count"] == 94

    # 2. Top categories & primary issues
    assert len(stats["top_categories"]) > 0
    assert len(stats["top_primary_issues"]) >= 5

    # 3. Top products
    assert len(stats["top_products"]) > 0
    top_p = stats["top_products"][0]
    assert top_p["sku"] == "VA-EB-PL2"
    assert top_p["ticket_count"] == 80

    # 4. Repeat contacts
    assert "repeat_contacts" in stats
    rep = stats["repeat_contacts"]
    assert rep["repeat_tickets_count"] == 67
    assert rep["repeat_contact_rate_pct"] == 33.67

    # 5. SLA performance
    assert "sla_performance" in stats
    assert stats["sla_performance"]["total_breaches"] == 15
    assert stats["sla_performance"]["overall_breach_rate_pct"] == 7.54
    assert stats["sla_performance"]["store_credit_cost_inr"] == 15 * 350

    # 6. Outcomes
    assert "outcomes" in stats
    assert stats["outcomes"]["refund_tickets_count"] == 30
    assert stats["outcomes"]["total_refund_amount_inr"] == 125797.0
    assert stats["outcomes"]["replacement_tickets_count"] == 24
    assert stats["outcomes"]["total_transfers_count"] == 21

    # 7. Operational Costs
    assert "operational_costs" in stats
    costs = stats["operational_costs"]
    assert costs["sla_breach_store_credit_cost_inr"] == 5250.0
    assert costs["direct_refund_payouts_inr"] == 125797.0
    assert costs["replacement_shipping_cost_inr"] == 8160.0
    assert costs["internal_transfer_handling_cost_inr"] == 6405.0
    assert costs["total_measurable_cost_inr"] == 198632.0


def test_partial_week_insufficient_data_detection(prepared_digest_data):
    """Verify that partial weeks (< 7 days) are correctly detected and flagged."""
    df, products, orders = prepared_digest_data
    stats_w27 = calculate_single_week_metrics(df, "2026-W27", products, orders)

    assert stats_w27["week"] == "2026-W27"
    assert stats_w27["days_covered"] == 2
    assert stats_w27["is_complete_week"] is False
    assert stats_w27["total_tickets"] == 46


def test_calculate_wow_changes(prepared_digest_data):
    """Verify week-over-week deltas and percentage shifts between W26 and W25."""
    df, products, orders = prepared_digest_data
    w26 = calculate_single_week_metrics(df, "2026-W26", products, orders)
    w25 = calculate_single_week_metrics(df, "2026-W25", products, orders)

    wow = calculate_wow_changes(w26, w25)

    assert wow["total_tickets"]["current"] == 199
    assert wow["total_tickets"]["previous"] == 167
    assert wow["total_tickets"]["absolute_change"] == 32
    assert wow["total_tickets"]["percentage_change"] == 19.16

    assert wow["repeat_rate_pct"]["current"] == 33.67
    assert wow["repeat_rate_pct"]["previous"] == 26.35
    assert wow["repeat_rate_pct"]["percentage_point_diff"] == 7.32

    assert wow["replacement_tickets"]["current"] == 24
    assert wow["replacement_tickets"]["previous"] == 14
    assert wow["replacement_tickets"]["absolute_change"] == 10


def test_build_deterministic_narrative_sections(prepared_digest_data):
    """Verify all 7 mandatory sections and factual tags are present in the generated markdown."""
    df, products, orders = prepared_digest_data
    w26 = calculate_single_week_metrics(df, "2026-W26", products, orders)
    w25 = calculate_single_week_metrics(df, "2026-W25", products, orders)
    wow = calculate_wow_changes(w26, w25)

    md = build_deterministic_narrative(w26, w25, wow)

    # 7 Mandatory Sections
    assert "## 1. EXECUTIVE SUMMARY" in md
    assert "## 2. TOP CUSTOMER COMPLAINTS" in md
    assert "## 3. WHAT CHANGED THIS WEEK" in md
    assert "## 4. PRODUCT / ISSUE CONCENTRATIONS" in md
    assert "## 5. OPERATIONAL COST SIGNALS" in md
    assert "## 6. WHAT DESERVES INVESTIGATION" in md
    assert "## 7. LIMITATIONS / DATA QUALITY NOTES" in md

    # Factual Labeling
    assert "[FACT]" in md
    assert "[HYPOTHESIS]" in md

    # Exact numbers verification
    assert "199 tickets" in md
    assert "33.67%" in md
    assert "7.54%" in md
    assert "₹125,797.00" in md
    assert "₹198,632.00" in md
    assert "VA-EB-PL2" in md


def test_pipeline_execution(tmp_path):
    """Integration test verifying full pipeline runs and creates valid JSON and Markdown files."""
    json_out = tmp_path / "test_digest.json"
    md_out = tmp_path / "test_digest.md"

    data, md_text = run_digest_pipeline(
        target_week_arg="2026-W26",
        provider="deterministic",
        output_json_path=json_out,
        output_md_path=md_out,
    )

    assert json_out.is_file()
    assert md_out.is_file()

    with open(json_out, "r", encoding="utf-8") as f:
        loaded_json = json.load(f)

    assert loaded_json["metadata"]["target_week"] == "2026-W26"
    assert loaded_json["target_week_metrics"]["total_tickets"] == 199
    assert len(loaded_json["all_weeks_telemetry"]) > 70
    assert "## 1. EXECUTIVE SUMMARY" in md_text
