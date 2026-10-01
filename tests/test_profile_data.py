"""Unit and Integration Tests for scripts/01_profile_data.py
Tests validation functions, integrity checks, timestamp parsing, and reporting logic.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Load scripts/01_profile_data.py dynamically
repo_root = Path(__file__).resolve().parent.parent
script_path = repo_root / "scripts" / "01_profile_data.py"

spec = importlib.util.spec_from_file_location("profile_data_mod", script_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["profile_data_mod"] = mod
spec.loader.exec_module(mod)

load_csv_safely = mod.load_csv_safely
profile_dataframe = mod.profile_dataframe
parse_ticket_timestamps = mod.parse_ticket_timestamps
validate_ticket_date_range = mod.validate_ticket_date_range
validate_referential_integrity = mod.validate_referential_integrity
check_data_integrity_rules = mod.check_data_integrity_rules
investigate_legacy_reimports = mod.investigate_legacy_reimports
evaluate_order_fallback_join = mod.evaluate_order_fallback_join
inspect_agents_roster = mod.inspect_agents_roster
run_full_audit = mod.run_full_audit
find_data_file = mod.find_data_file


@pytest.fixture
def sample_customers():
    return pd.DataFrame(
        {
            "customer_id": ["C101", "C102", "C103"],
            "name": ["Alice", "Bob", "Charlie"],
            "city": ["Bengaluru", "Indore", "Delhi"],
            "state": ["KA", "MP", "DL"],
            "signup_date": ["2024-01-01", "2024-02-01", "2024-03-01"],
            "care_plus": ["Y", "N", "Y"],
        }
    )


@pytest.fixture
def sample_products():
    return pd.DataFrame(
        {
            "sku": ["SKU-1", "SKU-2"],
            "product_name": ["Prod 1", "Prod 2"],
            "family": ["Earbuds", "Neckbands"],
            "launch_date": ["2023-01-01", "2023-06-01"],
            "unit_cost_inr": [1000, 1500],
            "retail_price_inr": [2500, 3500],
            "warranty_months": [12, 12],
        }
    )


@pytest.fixture
def sample_agents():
    return pd.DataFrame(
        {
            "agent_id": ["A1", "A2"],
            "name": ["Agent 1", "Agent 2"],
            "site": ["Bengaluru", "Indore"],
            "team": ["Chat Frontline", "Escalations & Warranty"],
            "shift": ["Morning", "Day"],
            "tier": [1, 2],
            "from_date": ["2023-01-01", "2023-01-01"],
            "to_date": [np.nan, np.nan],
        }
    )


@pytest.fixture
def sample_orders():
    return pd.DataFrame(
        {
            "order_id": ["ORD-1", "ORD-2", "ORD-3"],
            "customer_id": ["C101", "C102", "C101"],
            "sku": ["SKU-1", "SKU-2", "SKU-1"],
            "order_date": ["2025-01-01", "2025-02-01", "2025-03-01"],
            "channel": ["web", "app", "web"],
            "qty": [1, 1, 1],
            "order_value_inr": [2500, 3500, 2500],
            "lot_code": ["LOT1", "LOT2", "LOT3"],
        }
    )


@pytest.fixture
def sample_tickets():
    return pd.DataFrame(
        {
            "ticket_id": ["TK-1", "TK-2", "TK-3"],
            "created_at": ["2025-01-10 10:00", "2025-02-15 11:00", "2025-03-20 12:00"],
            "first_response_at": ["2025-01-10 10:10", "2025-02-15 11:20", "2025-03-20 12:15"],
            "resolved_at": ["2025-01-10 12:00", "2025-02-15 14:00", np.nan],
            "status": ["resolved", "closed", "open"],
            "channel": ["chat", "email", "voice"],
            "customer_id": ["C101", "C102", "C103"],
            "order_id": ["ORD-1", "ORD-2", np.nan],
            "product_sku": ["SKU-1", "SKU-2", "SKU-1"],
            "category": ["Audio Quality", "Delivery & Shipping", "Account & Login"],
            "priority": ["Normal", "High", "Low"],
            "assigned_team": ["Chat Frontline", "Logistics", "Voice Frontline"],
            "agent_id": ["A1", "A2", "A1"],
            "transfers": [0, 1, 0],
            "csat_score": [5.0, 4.0, np.nan],
            "refund_amount_inr": [np.nan, 3500.0, np.nan],
            "refund_reason_code": [np.nan, "LOST-TRANSIT", np.nan],
            "replacement_issued": ["N", "N", "N"],
            "customer_message": ["Help me", "Where is my order", "Cannot login"],
            "agent_notes": ["Resolved", "Refunded", "Investigating"],
            "source_system": ["helpdesk", "helpdesk", "helpdesk"],
        }
    )


def test_load_csv_safely_real_data():
    """Verify that all actual CSVs load safely without errors."""
    for fname in ["tickets.csv", "agents.csv", "customers.csv", "orders.csv", "products.csv"]:
        fpath = find_data_file(fname)
        df = load_csv_safely(fpath)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


def test_load_csv_safely_error_handling(tmp_path):
    """Verify error handling on non-existent and empty files."""
    missing_file = tmp_path / "non_existent.csv"
    with pytest.raises(FileNotFoundError):
        load_csv_safely(missing_file)

    empty_file = tmp_path / "empty.csv"
    empty_file.touch()
    with pytest.raises(ValueError, match="File is empty"):
        load_csv_safely(empty_file)


def test_profile_dataframe(sample_tickets):
    """Verify profiling metrics calculation."""
    profile = profile_dataframe(sample_tickets, "tickets", ["ticket_id", "customer_id"])
    assert profile["row_count"] == 3
    assert profile["column_count"] == 21
    assert profile["duplicate_rows"] == 0
    assert profile["unique_id_counts"]["ticket_id"] == 3
    assert profile["columns"]["order_id"]["missing_count"] == 1
    assert profile["columns"]["order_id"]["missing_percentage"] == 33.33


def test_parse_ticket_timestamps(sample_tickets):
    """Verify timestamps are parsed and localized into IST (+05:30)."""
    parsed = parse_ticket_timestamps(sample_tickets)
    assert "created_at_ist" in parsed.columns
    assert "first_response_at_ist" in parsed.columns
    assert "resolved_at_ist" in parsed.columns

    ist_val = parsed["created_at_ist"].iloc[0]
    assert ist_val.tzinfo.zone == "Asia/Kolkata"
    assert ist_val.strftime("%z") == "+0530"


def test_validate_ticket_date_range(sample_tickets):
    """Verify date range validation logic."""
    val = validate_ticket_date_range(sample_tickets, "2025-01-01", "2026-06-30")
    assert val["range_valid"] is True
    assert val["tickets_outside_expected_created_range"] == 0

    # Test with ticket outside range
    out_of_bounds = sample_tickets.copy()
    out_of_bounds.loc[0, "created_at"] = "2024-12-31 23:59"
    val_oob = validate_ticket_date_range(out_of_bounds, "2025-01-01", "2026-06-30")
    assert val_oob["range_valid"] is False
    assert val_oob["tickets_outside_expected_created_range"] == 1


def test_validate_referential_integrity(
    sample_tickets, sample_customers, sample_orders, sample_products, sample_agents
):
    """Verify referential integrity checks pass for clean data and fail on orphan FKs."""
    res = validate_referential_integrity(
        sample_tickets, sample_customers, sample_orders, sample_products, sample_agents
    )
    assert res["tickets_to_customers"]["valid"] is True
    assert res["tickets_to_orders"]["valid"] is True
    assert res["tickets_to_products"]["valid"] is True
    assert res["tickets_to_agents"]["valid"] is True

    # Inject orphan customer
    corrupted_tickets = sample_tickets.copy()
    corrupted_tickets.loc[0, "customer_id"] = "NON_EXISTENT_CUST"
    res_corrupted = validate_referential_integrity(
        corrupted_tickets, sample_customers, sample_orders, sample_products, sample_agents
    )
    assert res_corrupted["tickets_to_customers"]["valid"] is False
    assert res_corrupted["tickets_to_customers"]["orphan_count"] == 1


def test_check_data_integrity_rules(
    sample_tickets, sample_orders, sample_customers, sample_products, sample_agents
):
    """Verify check_data_integrity_rules correctly detects anomalies."""
    rules = check_data_integrity_rules(
        sample_tickets, sample_orders, sample_customers, sample_products, sample_agents
    )
    assert rules["status_consistency"]["valid"] is True
    assert rules["csat_metrics"]["csat_out_of_range"] == 0
    assert rules["refund_metrics"]["negative_refunds"] == 0

    # Inject bad values
    bad_tickets = sample_tickets.copy()
    bad_tickets.loc[0, "status"] = "resolved"
    bad_tickets.loc[0, "resolved_at"] = np.nan  # resolved without resolved_at
    bad_tickets.loc[1, "refund_amount_inr"] = -100.0  # negative refund
    bad_tickets.loc[2, "status"] = "INVALID_STATUS"  # invalid status

    bad_rules = check_data_integrity_rules(
        bad_tickets, sample_orders, sample_customers, sample_products, sample_agents
    )
    assert bad_rules["status_consistency"]["resolved_or_closed_without_resolved_at"] == 1
    assert bad_rules["refund_metrics"]["negative_refunds"] == 1
    assert "INVALID_STATUS" in bad_rules["categorical_validity"]["invalid_statuses"]


def test_investigate_legacy_reimports():
    """Verify detection of duplicate tickets across source systems."""
    t_data = pd.DataFrame(
        {
            "ticket_id": ["TK-100", "TK-100", "TK-101"],
            "created_at": ["2025-01-01 10:00", "2025-01-01 10:00", "2025-01-02 10:00"],
            "first_response_at": ["2025-01-01 11:00", "2025-01-01 11:00", "2025-01-02 11:00"],
            "resolved_at": ["2025-01-01 15:30", "2025-01-01 10:00", "2025-01-02 15:00"],  # 5h30m diff
            "status": ["resolved", "resolved", "resolved"],
            "channel": ["email", "email", "email"],
            "customer_id": ["C1", "C1", "C2"],
            "order_id": [np.nan, np.nan, np.nan],
            "product_sku": ["SKU1", "SKU1", "SKU2"],
            "category": ["Other", "Other", "Other"],
            "priority": ["Low", "Low", "Low"],
            "assigned_team": ["Email Frontline", "Email Frontline", "Email Frontline"],
            "agent_id": ["A1", "A1", "A2"],
            "transfers": [0, 0, 0],
            "csat_score": [np.nan, 0.0, 5.0],  # NaN vs 0.0
            "refund_amount_inr": [np.nan, np.nan, np.nan],
            "refund_reason_code": [np.nan, np.nan, np.nan],
            "replacement_issued": ["N", "N", "N"],
            "customer_message": ["msg", "msg", "msg2"],
            "agent_notes": ["notes", "notes", "notes2"],
            "source_system": ["helpdesk", "legacy_fd", "helpdesk"],
        }
    )
    res = investigate_legacy_reimports(t_data)
    assert res["duplicated_ticket_ids_count"] == 1
    assert res["total_duplicated_rows"] == 2
    assert res["resolved_at_utc_to_ist_offset_verified_count"] == 1
    assert res["column_discrepancies_between_systems"]["csat_score"] == 1


def test_evaluate_order_fallback_join(sample_tickets, sample_orders):
    """Verify fallback join matches tickets missing order_id using (customer_id, product_sku)."""
    res = evaluate_order_fallback_join(sample_tickets, sample_orders)
    assert res["missing_order_id_count"] == 1
    assert res["zero_matches_count"] == 1

    t_mod = sample_tickets.copy()
    t_mod.loc[2, "customer_id"] = "C101"
    t_mod.loc[2, "product_sku"] = "SKU-1"
    res_mod = evaluate_order_fallback_join(t_mod, sample_orders)
    assert res_mod["multiple_matches_count"] == 1


def test_inspect_agents_roster(sample_agents):
    """Verify roster inspection logic and warning output."""
    res = inspect_agents_roster(sample_agents)
    assert res["total_roster_rows"] == 2
    assert res["unique_agent_ids"] == 2
    assert res["active_assignments_count"] == 2
    assert "SCD" in res["schema_semantics_warning"]


def test_full_audit_execution():
    """Integration test verifying full audit executes on real files and produces required outputs."""
    report = run_full_audit()
    assert report is not None
    assert "profiles" in report
    assert "categorized_findings" in report
    assert len(report["categorized_findings"]["confirmed_data_problems"]) > 0
    assert len(report["categorized_findings"]["expected_behaviors"]) > 0
    assert len(report["categorized_findings"]["requires_investigation"]) > 0
