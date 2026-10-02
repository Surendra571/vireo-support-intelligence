"""tests/test_evaluation.py - Unit and integration tests for scripts/05_evaluate.py.

Validates gold benchmark stratification, accuracy measurement mechanics,
independent deterministic assertions, and required report distinctions.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
import pandas as pd
import pytest

# Dynamic import of scripts/05_evaluate.py
repo_root = Path(__file__).resolve().parent.parent
script_path = repo_root / "scripts" / "05_evaluate.py"

spec = importlib.util.spec_from_file_location("evaluate_mod", script_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["evaluate_mod"] = mod
spec.loader.exec_module(mod)

load_evaluation_data = mod.load_evaluation_data
evaluate_ai_classification = mod.evaluate_ai_classification
run_independent_deterministic_validation = mod.run_independent_deterministic_validation
generate_evaluation_artifacts = mod.generate_evaluation_artifacts


# ==============================================================================
# 1. GOLD BENCHMARK SAMPLE & STRATIFICATION TESTS
# ==============================================================================

def test_gold_benchmark_sample_properties():
    """Verify gold benchmark has >= 100 tickets, full stratification, and valid taxonomy."""
    gold_path = repo_root / "data" / "gold_labels_sample.csv"
    assert gold_path.is_file(), f"Gold benchmark file missing: {gold_path}"

    df = pd.read_csv(gold_path)

    # 1. Sample size >= 100
    assert len(df) >= 100, f"Expected >= 100 tickets, got {len(df)}"
    assert len(df) == 120

    # 2. Stratification across all 4 channels
    channels = set(df["channel"].str.lower().unique())
    assert {"chat", "email", "voice", "social"}.issubset(channels)
    for ch in ["chat", "email", "voice", "social"]:
        assert (df["channel"].str.lower() == ch).sum() >= 10

    # 3. Stratification across all major categories
    categories = set(df["category"].unique())
    expected_categories = {
        "Delivery & Shipping",
        "Connectivity",
        "Charging & Battery",
        "Billing & Payments",
        "Returns & Refunds",
        "App & Firmware",
        "Audio Quality",
        "Warranty & Repair",
        "Product Enquiry",
        "Account & Login",
        "Other",
    }
    assert expected_categories.issubset(categories)

    # 4. Stratum diversity (ambiguous, multi_issue, short_message, long_message, standard)
    strata = set(df["stratum"].unique())
    assert {"ambiguous", "multi_issue", "short_message", "long_message", "standard"}.issubset(strata)
    for s in ["ambiguous", "multi_issue", "short_message", "long_message"]:
        assert (df["stratum"] == s).sum() >= 15

    # 5. Schema completeness
    required_cols = [
        "ticket_id",
        "channel",
        "product_sku",
        "category",
        "stratum",
        "gold_primary_issue",
        "gold_secondary_issue",
        "gold_customer_intent",
        "gold_resolution_type",
        "gold_repeat_contact_signal",
        "gold_root_cause_signal",
        "gold_rationale",
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"


# ==============================================================================
# 2. AI ACCURACY EVALUATION CALCULATION TESTS
# ==============================================================================

def test_ai_accuracy_evaluation_computation():
    """Verify evaluation metric calculations produce mathematically valid bounds."""
    gold_path = repo_root / "data" / "gold_labels_sample.csv"
    classified_path = repo_root / "outputs" / "classified_tickets.csv"

    gold_df, class_df, merged_df = load_evaluation_data(gold_path, classified_path)
    assert len(merged_df) == len(gold_df)

    results = evaluate_ai_classification(merged_df)

    assert results["sample_size"] == len(gold_df)
    assert 0.0 <= results["overall_exact_match_all_fields"]["accuracy_pct"] <= 100.0

    # Verify all 5 core fields have measured metrics
    for field in ["primary_issue", "customer_intent", "resolution_type", "repeat_contact_signal", "root_cause_signal"]:
        m = results["field_metrics"][field]
        assert m["correct"] + m["errors"] == results["sample_size"]
        assert 0.0 <= m["accuracy_pct"] <= 100.0
        assert isinstance(m["top_confusion_pairs"], list)

    # Verify per-category breakdown
    cat_acc = results["per_category_accuracy"]
    assert len(cat_acc) == 11
    for cat, stats in cat_acc.items():
        assert stats["total_tickets"] > 0
        assert 0.0 <= stats["accuracy_pct"] <= 100.0


# ==============================================================================
# 3. DETERMINISTIC INDEPENDENT VALIDATION TESTS
# ==============================================================================

def test_deterministic_validation_assertions_pass():
    """Verify that independent deterministic validation runs all 8 assertions and passes 100%."""
    tickets_path = repo_root / "data" / "tickets.csv"
    agents_path = repo_root / "data" / "agents.csv"
    business_metrics_path = repo_root / "outputs" / "business_metrics.json"
    agent_metrics_path = repo_root / "outputs" / "agent_weekly_metrics.csv"

    det_results = run_independent_deterministic_validation(
        tickets_path=tickets_path,
        agents_path=agents_path,
        business_metrics_path=business_metrics_path,
        agent_metrics_path=agent_metrics_path,
    )

    assert det_results["status"] == "ALL_ASSERTIONS_PASSED"
    assert det_results["total_assertions"] == 8
    assert det_results["passed_assertions"] == 8
    assert det_results["failed_assertions"] == 0

    # Ensure all 8 dimensions are checked
    dimensions = [x["dimension"] for x in det_results["verification_details"]]
    assert "Total Analyzed Tickets" in dimensions
    assert "Weekly Operational Counts" in dimensions
    assert "First-Response SLA Breaches & Store Credits" in dimensions
    assert "Refund Volume & Financial Disbursements" in dimensions
    assert "Replacement Logistics & Volume" in dimensions
    assert "Internal Transfers & Friction Cost" in dimensions
    assert "Agent Closures & Weekly Roster Rollup" in dimensions
    assert "Repeat Contacts (Support Policy Method A)" in dimensions


# ==============================================================================
# 4. REPORT & GOVERNANCE STRUCTURE TESTS
# ==============================================================================

def test_evaluation_artifacts_and_governance_distinctions():
    """Verify generated JSON and markdown report contain mandatory distinctions."""
    out_json_path = repo_root / "outputs" / "evaluation_results.json"
    out_md_path = repo_root / "outputs" / "evaluation_report.md"

    assert out_json_path.is_file(), f"Output JSON missing: {out_json_path}"
    assert out_md_path.is_file(), f"Output Markdown missing: {out_md_path}"

    with open(out_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "ai_classification_evaluation" in data
    assert "deterministic_analytics_validation" in data
    assert "evaluation_governance" in data

    md_text = out_md_path.read_text(encoding="utf-8")

    # Verify mandatory governance headers
    assert "EXECUTIVE SUMMARY" in md_text
    assert "PART A: AI CLASSIFICATION ACCURACY EVALUATION" in md_text
    assert "PART B: DETERMINISTIC ANALYTICS INDEPENDENT VALIDATION" in md_text
    assert "MEASURED ERROR" in md_text
    assert "KNOWN LIMITATION" in md_text
    assert "UNRESOLVED UNCERTAINTY" in md_text
