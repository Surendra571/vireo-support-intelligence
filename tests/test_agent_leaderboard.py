"""Unit and integration tests for scripts/05_agent_leaderboard.py.
Tests roster validity ranges, Tier 2 exclusion from Tier 1 ranking,
inclusion of resolved/closed, exclusion of open/pending, and ambiguity handling.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

# Dynamically import scripts/05_agent_leaderboard.py
repo_root = Path(__file__).resolve().parent.parent
script_path = repo_root / "scripts" / "05_agent_leaderboard.py"

spec = importlib.util.spec_from_file_location("agent_leaderboard_mod", script_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["agent_leaderboard_mod"] = mod
spec.loader.exec_module(mod)

match_agent_roster_row = mod.match_agent_roster_row
build_agent_weekly_metrics = mod.build_agent_weekly_metrics
run_leaderboard_pipeline = mod.run_leaderboard_pipeline


# ==============================================================================
# 1. ROSTER CHANGES & VALIDITY RANGE TESTS
# ==============================================================================
def test_roster_changes_across_dates():
    """Verify that an agent with multiple roster records is correctly assigned to

    the applicable team, tier, site, and shift on the ticket closure date.
    """
    roster_df = pd.DataFrame(
        [
            {
                "agent_id": "A9001",
                "name": "Test Agent",
                "site": "Indore",
                "team": "Chat Frontline",
                "shift": "Morning",
                "tier": 1,
                "from_date": "2025-01-01",
                "to_date": "2025-06-30",
            },
            {
                "agent_id": "A9001",
                "name": "Test Agent",
                "site": "Bengaluru",
                "team": "Email Frontline",
                "shift": "Day",
                "tier": 1,
                "from_date": "2025-07-01",
                "to_date": "2025-12-31",
            },
            {
                "agent_id": "A9001",
                "name": "Test Agent",
                "site": "Bengaluru",
                "team": "Escalations & Warranty",
                "shift": "Day",
                "tier": 2,
                "from_date": "2026-01-01",
                "to_date": None,  # Ongoing
            },
        ]
    )

    # Date in Period 1
    match1, warn1 = match_agent_roster_row("A9001", pd.Timestamp("2025-03-15"), roster_df)
    assert warn1 is None
    assert match1["team"] == "Chat Frontline"
    assert match1["site"] == "Indore"
    assert match1["shift"] == "Morning"
    assert match1["tier"] == 1

    # Date in Period 2
    match2, warn2 = match_agent_roster_row("A9001", pd.Timestamp("2025-09-20"), roster_df)
    assert warn2 is None
    assert match2["team"] == "Email Frontline"
    assert match2["site"] == "Bengaluru"
    assert match2["shift"] == "Day"
    assert match2["tier"] == 1

    # Date in Period 3 (Promoted to Tier 2)
    match3, warn3 = match_agent_roster_row("A9001", pd.Timestamp("2026-03-10"), roster_df)
    assert warn3 is None
    assert match3["team"] == "Escalations & Warranty"
    assert match3["tier"] == 2


def test_roster_ambiguity_and_out_of_bounds_handling():
    """Verify that overlapping roster assignments or unassigned dates report ambiguity

    rather than silently assigning an arbitrary team.
    """
    overlapping_roster = pd.DataFrame(
        [
            {
                "agent_id": "A9002",
                "name": "Overlapping Agent",
                "site": "Indore",
                "team": "Chat Frontline",
                "shift": "Morning",
                "tier": 1,
                "from_date": "2025-01-01",
                "to_date": "2025-06-30",
            },
            {
                "agent_id": "A9002",
                "name": "Overlapping Agent",
                "site": "Indore",
                "team": "Voice Frontline",
                "shift": "Evening",
                "tier": 1,
                "from_date": "2025-05-01",  # Overlaps with row 1 in May and June
                "to_date": "2025-10-31",
            },
        ]
    )

    # Date in overlap window (e.g. 2025-05-15)
    matched, warning = match_agent_roster_row("A9002", pd.Timestamp("2025-05-15"), overlapping_roster)
    assert warning is not None
    assert "Ambiguous roster assignment" in warning
    assert matched["team"] == "Ambiguous / Multiple Roster Matches"

    # Date before all roster records (2024-12-01)
    matched_oob, warning_oob = match_agent_roster_row("A9002", pd.Timestamp("2024-12-01"), overlapping_roster)
    assert warning_oob is not None
    assert "no valid roster assignment" in warning_oob
    assert matched_oob["team"] == "Unassigned / Out of Roster Range"


# ==============================================================================
# 2. TIER 2 EXCLUSION FROM TIER 1 RANKING
# ==============================================================================
def test_tier_2_exclusion_from_tier_1_ranking():
    """Verify that Tier 2 agents are NEVER ranked against Tier 1 agents per Support Policy §6."""
    roster_df = pd.DataFrame(
        [
            {"agent_id": "T1_A", "name": "Agent 1", "site": "Indore", "team": "Chat Frontline", "shift": "Day", "tier": 1, "from_date": "2025-01-01", "to_date": None},
            {"agent_id": "T1_B", "name": "Agent 2", "site": "Indore", "team": "Chat Frontline", "shift": "Day", "tier": 1, "from_date": "2025-01-01", "to_date": None},
            {"agent_id": "T2_A", "name": "Warranty 1", "site": "Bengaluru", "team": "Escalations & Warranty", "shift": "Day", "tier": 2, "from_date": "2025-01-01", "to_date": None},
        ]
    )

    # Synthetic tickets for same week 2025-W10:
    # T1_A closes 5 tickets
    # T1_B closes 3 tickets
    # T2_A closes 20 tickets (even if higher volume, must NOT be ranked against Tier 1)
    tickets = []
    # 5 tickets for T1_A
    for i in range(5):
        tickets.append({
            "ticket_id": f"TK-T1A-{i}",
            "status": "resolved",
            "agent_id": "T1_A",
            "created_at": "2025-03-03 10:00",
            "resolved_at": "2025-03-03 11:00",
            "first_response_at": "2025-03-03 10:05",
            "channel": "chat",
            "transfers": 0,
            "csat_score": 5.0,
        })
    # 3 tickets for T1_B
    for i in range(3):
        tickets.append({
            "ticket_id": f"TK-T1B-{i}",
            "status": "resolved",
            "agent_id": "T1_B",
            "created_at": "2025-03-03 10:00",
            "resolved_at": "2025-03-03 11:00",
            "first_response_at": "2025-03-03 10:05",
            "channel": "chat",
            "transfers": 0,
            "csat_score": 4.0,
        })
    # 20 tickets for T2_A
    for i in range(20):
        tickets.append({
            "ticket_id": f"TK-T2A-{i}",
            "status": "resolved",
            "agent_id": "T2_A",
            "created_at": "2025-03-03 10:00",
            "resolved_at": "2025-03-03 11:00",
            "first_response_at": "2025-03-03 10:05",
            "channel": "chat",
            "transfers": 0,
            "csat_score": 5.0,
        })

    t_df = pd.DataFrame(tickets)
    t_df["created_at_dt"] = pd.to_datetime(t_df["created_at"])
    t_df["first_response_at_dt"] = pd.to_datetime(t_df["first_response_at"])
    t_df["resolved_at_dt"] = pd.to_datetime(t_df["resolved_at"])
    t_df["is_repeat"] = False
    t_df["sla_breached"] = False

    metrics, _ = build_agent_weekly_metrics(t_df, roster_df)

    # Check Tier 1
    t1_records = metrics[metrics["tier"] == 1]
    assert len(t1_records) == 2

    # T1_A must be Rank #1 in Tier 1 with 5 tickets
    t1_a_row = t1_records[t1_records["agent_id"] == "T1_A"].iloc[0]
    assert t1_a_row["tickets_closed"] == 5
    assert t1_a_row["tier_1_rank"] == 1
    assert pd.isna(t1_a_row["tier_2_rank"])

    # T1_B must be Rank #2 in Tier 1 with 3 tickets
    t1_b_row = t1_records[t1_records["agent_id"] == "T1_B"].iloc[0]
    assert t1_b_row["tickets_closed"] == 3
    assert t1_b_row["tier_1_rank"] == 2
    assert pd.isna(t1_b_row["tier_2_rank"])

    # Check Tier 2
    t2_records = metrics[metrics["tier"] == 2]
    assert len(t2_records) == 1
    t2_row = t2_records.iloc[0]
    assert t2_row["agent_id"] == "T2_A"
    assert t2_row["tickets_closed"] == 20
    assert pd.isna(t2_row["tier_1_rank"])  # Excluded from Tier 1 rank
    assert t2_row["tier_2_rank"] == 1      # Only ranked within Tier 2


# ==============================================================================
# 3. RESOLVED VS CLOSED (BOTH COUNTED) & OPEN/PENDING EXCLUSION
# ==============================================================================
def test_status_inclusion_resolved_closed_and_exclusion_open_pending():
    """Verify that tickets with status 'resolved' and 'closed' are counted in completed attendance,

    while tickets with status 'open' and 'pending' are strictly excluded.
    """
    roster_df = pd.DataFrame(
        [
            {"agent_id": "A100", "name": "Agent 100", "site": "Indore", "team": "Chat Frontline", "shift": "Day", "tier": 1, "from_date": "2025-01-01", "to_date": None},
        ]
    )

    tickets = [
        # 2 Resolved tickets -> Counted
        {"ticket_id": "TK-1", "status": "resolved", "agent_id": "A100", "created_at": "2025-02-01 10:00", "resolved_at": "2025-02-01 11:00", "first_response_at": "2025-02-01 10:05", "channel": "chat", "transfers": 0, "csat_score": 4.0},
        {"ticket_id": "TK-2", "status": "resolved", "agent_id": "A100", "created_at": "2025-02-01 12:00", "resolved_at": "2025-02-01 13:00", "first_response_at": "2025-02-01 12:05", "channel": "chat", "transfers": 0, "csat_score": 5.0},
        # 1 Closed ticket -> Counted
        {"ticket_id": "TK-3", "status": "closed", "agent_id": "A100", "created_at": "2025-02-01 14:00", "resolved_at": "2025-02-01 15:00", "first_response_at": "2025-02-01 14:05", "channel": "chat", "transfers": 0, "csat_score": 4.0},
        # 1 Open ticket -> MUST BE EXCLUDED
        {"ticket_id": "TK-4", "status": "open", "agent_id": "A100", "created_at": "2025-02-01 16:00", "resolved_at": np.nan, "first_response_at": "2025-02-01 16:05", "channel": "chat", "transfers": 0, "csat_score": np.nan},
        # 1 Pending ticket -> MUST BE EXCLUDED
        {"ticket_id": "TK-5", "status": "pending", "agent_id": "A100", "created_at": "2025-02-01 17:00", "resolved_at": np.nan, "first_response_at": "2025-02-01 17:05", "channel": "chat", "transfers": 0, "csat_score": np.nan},
    ]

    t_df = pd.DataFrame(tickets)
    t_df["created_at_dt"] = pd.to_datetime(t_df["created_at"])
    t_df["first_response_at_dt"] = pd.to_datetime(t_df["first_response_at"])
    t_df["resolved_at_dt"] = pd.to_datetime(t_df["resolved_at"])
    t_df["is_repeat"] = False
    t_df["sla_breached"] = False

    metrics, _ = build_agent_weekly_metrics(t_df, roster_df)

    assert len(metrics) == 1
    row = metrics.iloc[0]
    # Total tickets closed must be exactly 3 (2 resolved + 1 closed), open and pending are excluded
    assert row["tickets_closed"] == 3


def test_full_agent_leaderboard_pipeline_real_data(tmp_path):
    """Integration test verifying full leaderboard runs on real data and produces valid CSV and MD."""
    csv_out = tmp_path / "test_agent_metrics.csv"
    md_out = tmp_path / "test_agent_leaderboard.md"

    metrics_df = run_leaderboard_pipeline(
        output_csv_path=csv_out,
        output_md_path=md_out,
        target_week="2026-W26",
    )

    assert csv_out.is_file()
    assert md_out.is_file()

    # Verify CSV schema
    loaded_csv = pd.read_csv(csv_out)
    required_cols = [
        "week",
        "agent_id",
        "team",
        "tier",
        "site",
        "shift",
        "tickets_closed",
        "sla_breaches",
        "repeat_contacts",
        "csat_response_count",
        "csat_average",
    ]
    for col in required_cols:
        assert col in loaded_csv.columns

    # Verify Tier 2 exclusion in rankings
    tier_1_subset = loaded_csv[loaded_csv["tier"] == 1]
    tier_2_subset = loaded_csv[loaded_csv["tier"] == 2]

    assert tier_1_subset["tier_1_rank"].notna().all()
    assert tier_1_subset["tier_2_rank"].isna().all()

    assert tier_2_subset["tier_2_rank"].notna().all()
    assert tier_2_subset["tier_1_rank"].isna().all()

    # Verify Markdown contents
    with open(md_out, "r", encoding="utf-8") as f:
        md_text = f.read()

    assert "TIER 1 FRONTLINE LEADERBOARD" in md_text
    assert "TIER 2 ESCALATIONS & WARRANTY ACTIVITY (NOT RANKED AGAINST TIER 1)" in md_text
    assert "TICKETS CLOSED IS NOT AN OVERALL PERFORMANCE SCORE" in md_text
