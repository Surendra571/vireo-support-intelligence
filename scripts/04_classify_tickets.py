"""scripts/04_classify_tickets.py

Vireo Audio Support Intelligence — Step 4: AI-Assisted Ticket Classification
=============================================================================
Production-minded AI-assisted ticket classification pipeline that converts each
customer support ticket/message into structured, auditable fields for downstream
weekly digest generation and thematic trend analysis.

Features:
  - Deterministic preprocessing and deduplication.
  - Strict controlled taxonomy derived from empirical Vireo support tickets.
  - Separate explicit text-based repeat-contact signal detector (captures customer protest
    language without claiming premature closure causality or agent fault).
  - Explicit 3-tier confidence policy (High >=0.80, Medium 0.60-0.79, Low <0.60).
  - Resilient error containment and deterministic fallback (zero crash guarantee).
  - SQLite-backed persistent caching with content hashing (SHA-256).
  - Generates outputs/classified_tickets.csv preserving all required schema fields.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

# Add repo root to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from app.services.classifier import (
    ALLOWED_CUSTOMER_INTENTS,
    ALLOWED_PRIMARY_ISSUES,
    BaseLLMClient,
    ClassificationCache,
    ClassifierService,
    GeminiLLMClient,
    OpenAILLMClient,
    RuleBasedTaxonomyClient,
    detect_repeat_signal,
)


def find_data_file(filename: str, search_dirs: Optional[List[Path]] = None) -> Path:
    """Locate a data file across standard search directories."""
    if search_dirs is None:
        base_dir = Path(__file__).resolve().parent.parent
        search_dirs = [
            base_dir / "data",
            base_dir,
            Path("data"),
            Path("."),
        ]

    for directory in search_dirs:
        candidate = directory / filename
        if candidate.is_file():
            return candidate

    raise FileNotFoundError(
        f"Could not find '{filename}' in search directories: {[str(d) for d in search_dirs]}"
    )


def load_clean_tickets(data_dir: Optional[Path] = None) -> pd.DataFrame:
    """Loads and deduplicates tickets.csv, prioritizing helpdesk over legacy_fd."""
    tickets_path = find_data_file("tickets.csv", [data_dir] if data_dir else None)
    df_raw = pd.read_csv(tickets_path, low_memory=False)

    df_clean = (
        df_raw.sort_values(by=["ticket_id", "source_system"], ascending=[True, True])
        .drop_duplicates(subset=["ticket_id"], keep="first")
        .copy()
    )
    return df_clean


def build_llm_client(provider: str, model_name: Optional[str] = None) -> BaseLLMClient:
    """Factory creating the requested LLM client."""
    provider_clean = provider.lower().strip()

    if provider_clean == "gemini":
        model = model_name or "gemini-2.5-flash"
        return GeminiLLMClient(model_name=model)
    elif provider_clean == "openai":
        model = model_name or "gpt-4o-mini"
        return OpenAILLMClient(model_name=model)
    elif provider_clean == "rule_based" or provider_clean == "local":
        model = model_name or "vireo-semantic-classifier-v1"
        return RuleBasedTaxonomyClient(model_name=model)
    elif provider_clean == "auto":
        if os.environ.get("GEMINI_API_KEY"):
            return GeminiLLMClient(model_name=model_name or "gemini-2.5-flash")
        elif os.environ.get("OPENAI_API_KEY"):
            return OpenAILLMClient(model_name=model_name or "gpt-4o-mini")
        else:
            return RuleBasedTaxonomyClient(model_name=model_name or "vireo-semantic-classifier-v1")
    else:
        raise ValueError(f"Unknown provider '{provider}'. Choose from: auto, gemini, openai, rule_based.")


def classify_tickets_batch(
    tickets_df: pd.DataFrame,
    service: ClassifierService,
    limit: Optional[int] = None,
    output_csv_path: Path | str = "outputs/classified_tickets.csv",
    progress_interval: int = 1000,
    bypass_cache: bool = False,
) -> pd.DataFrame:
    """Classifies a batch of tickets and saves the results to CSV conforming to Step 4 schema."""
    df_to_process = tickets_df.head(limit) if limit else tickets_df
    total_count = len(df_to_process)

    print(f"Starting Step 4 classification on {total_count:,} tickets using model: '{service.llm_client.model_name}'...")
    start_time = time.time()

    records = []
    cache_hits = 0

    for idx, (_, row) in enumerate(df_to_process.iterrows(), 1):
        ticket_dict = {
            "ticket_id": row.get("ticket_id"),
            "customer_id": row.get("customer_id"),
            "channel": row.get("channel"),
            "product_sku": row.get("product_sku"),
            "category": row.get("category"),
            "assigned_team": row.get("assigned_team"),
            "customer_message": row.get("customer_message"),
            "agent_notes": row.get("agent_notes"),
            "created_at": row.get("created_at"),
            "status": row.get("status"),
            "priority": row.get("priority"),
        }

        classification = service.classify_ticket(ticket_dict, bypass_cache=bypass_cache)
        meta = classification.get("_metadata", {})
        if meta.get("cached", False):
            cache_hits += 1

        record = {
            # 12 Mandatory Step 4 Schema Fields
            "ticket_id": row.get("ticket_id"),
            "customer_id": row.get("customer_id"),
            "product_sku": row.get("product_sku"),
            "channel": row.get("channel"),
            "created_at": row.get("created_at"),
            "primary_issue": classification.get("primary_issue", "unknown"),
            "secondary_issue": classification.get("secondary_issue"),
            "customer_intent": classification.get("customer_intent", "unknown"),
            "repeat_signal": bool(classification.get("repeat_signal", False)),
            "repeat_signal_reason": classification.get("repeat_signal_reason") or "",
            "confidence": float(classification.get("confidence", 0.0)),
            "classification_method": classification.get("classification_method", "unknown"),
            # Preserved Context & Deterministic Fields
            "category": row.get("category"),
            "assigned_team": row.get("assigned_team"),
            "status": row.get("status"),
            "priority": row.get("priority"),
            "customer_message": row.get("customer_message"),
            "agent_notes": row.get("agent_notes"),
            "resolution_type": classification.get("resolution_type"),
            "repeat_contact_signal": classification.get("repeat_contact_signal"),
            "root_cause_signal": classification.get("root_cause_signal"),
            "model": meta.get("model", service.llm_client.model_name),
            "prompt_version": meta.get("prompt_version", service.prompt_version),
            "classified_at": meta.get("timestamp"),
        }
        records.append(record)

        if idx % progress_interval == 0 or idx == total_count:
            elapsed = time.time() - start_time
            rate = idx / elapsed if elapsed > 0 else 0
            print(
                f"[{idx:,}/{total_count:,}] ({(idx/total_count*100):.1f}%) | "
                f"Cache hits: {cache_hits:,} | {rate:.1f} tickets/sec"
            )

    out_df = pd.DataFrame(records)
    out_path = Path(output_csv_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f"Successfully saved {len(out_df):,} classified tickets to: {out_path}")

    return out_df


def print_classification_summary(classified_df: pd.DataFrame, source_df: pd.DataFrame) -> None:
    """Prints a detailed quality audit of the Step 4 classification results."""
    total = len(classified_df)
    source_total = len(source_df)
    coverage_pct = round(total / source_total * 100, 2) if source_total > 0 else 0.0
    avg_conf = round(float(classified_df["confidence"].mean()), 3)

    # Confidence distribution
    high_conf = int((classified_df["confidence"] >= 0.80).sum())
    med_conf = int(((classified_df["confidence"] >= 0.60) & (classified_df["confidence"] < 0.80)).sum())
    low_conf = int((classified_df["confidence"] < 0.60).sum())

    # Repeat signals
    rep_count = int(classified_df["repeat_signal"].sum())
    rep_pct = round(rep_count / total * 100, 2) if total > 0 else 0.0

    # Fallbacks and missing
    fallback_count = int((classified_df["classification_method"] == "fallback_low_confidence").sum())
    cat_fallback_count = int((classified_df["classification_method"] == "category_fallback").sum())
    missing_issue_count = int(classified_df["primary_issue"].isna().sum() + (classified_df["primary_issue"] == "").sum())

    print("\n" + "=" * 80)
    print(" VIREO AUDIO STEP 4 AI TICKET CLASSIFICATION QUALITY REPORT")
    print("=" * 80)
    print(f"Total Source Unique Tickets: {source_total:,}")
    print(f"Total Classified Tickets   : {total:,}")
    print(f"Classification Coverage    : {coverage_pct}%")
    print(f"Average Model Confidence   : {avg_conf}")
    print(f"Model Identifier           : {classified_df['model'].iloc[0] if total > 0 else 'N/A'}")
    print(f"Prompt Version             : {classified_df['prompt_version'].iloc[0] if total > 0 else 'N/A'}")
    print("-" * 80)

    print("CONFIDENCE TIERS DISTRIBUTION:")
    print(f"  * High Confidence (>= 0.80)     : {high_conf:>5,} ({(high_conf/total*100):>5.1f}%) [Direct keyword / LLM match]")
    print(f"  * Medium Confidence (0.60-0.79) : {med_conf:>5,} ({(med_conf/total*100):>5.1f}%) [Category fallback]")
    print(f"  * Low Confidence (< 0.60)       : {low_conf:>5,} ({(low_conf/total*100):>5.1f}%) [Review queue / unmapped]")
    print(f"  * Low Confidence Fallback Count : {fallback_count:>5,} ({(fallback_count/total*100):>5.1f}%)")
    print(f"  * Missing / Invalid Issue Count : {missing_issue_count}")
    print("-" * 80)

    print("EXPLICIT REPEAT-CONTACT SIGNALS:")
    print(f"  * Explicit Repeat Signals Count : {rep_count:,} tickets ({rep_pct}%)")
    print(f"  * Reason Note                   : Explicit customer protest phrases in message text.")
    print("  * Cautionary Boundary           : Indicates customer-reported repetition, NOT proof of agent fault or premature closure.")
    print("-" * 80)

    print("PRIMARY ISSUES BREAKDOWN (Controlled Taxonomy):")
    for issue, cnt in classified_df["primary_issue"].value_counts().items():
        print(f"  * {issue:<32}: {cnt:>5,} ({(cnt/total*100):>5.1f}%)")

    print("\nCUSTOMER INTENTS BREAKDOWN:")
    for intent, cnt in classified_df["customer_intent"].value_counts().items():
        print(f"  * {intent:<32}: {cnt:>5,} ({(cnt/total*100):>5.1f}%)")

    print("-" * 80)
    print("SAMPLE CLASSIFICATIONS ACROSS CATEGORIES:")
    sample_categories = ["Delivery & Shipping", "Charging & Battery", "Connectivity", "Billing & Payments", "Returns & Refunds"]
    for cat in sample_categories:
        sub = classified_df[classified_df["category"] == cat]
        if not sub.empty:
            sample_row = sub.iloc[0]
            msg_snippet = str(sample_row["customer_message"]).replace("\n", " ")[:60]
            print(f"  [{cat}] Ticket: {sample_row['ticket_id']} | SKU: {sample_row['product_sku']}")
            print(f"    Message : \"{msg_snippet}...\"")
            print(f"    Issue   : {sample_row['primary_issue']} | Intent: {sample_row['customer_intent']}")
            print(f"    Method  : {sample_row['classification_method']} | Conf: {sample_row['confidence']} | Repeat Sig: {sample_row['repeat_signal']}")
    print("=" * 80 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Vireo Audio Step 4 Ticket Classifier")
    parser.add_argument("--provider", default="auto", help="LLM Provider: auto, gemini, openai, rule_based")
    parser.add_argument("--model", default=None, help="Model identifier")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of tickets to classify (for testing)")
    parser.add_argument("--output", default="outputs/classified_tickets.csv", help="Output CSV path")
    parser.add_argument("--data-dir", default=None, help="Directory containing tickets.csv")
    parser.add_argument("--bypass-cache", action="store_true", help="Force re-classification bypassing SQLite cache")
    args = parser.parse_args()

    # 1. Load Clean Tickets
    data_dir = Path(args.data_dir) if args.data_dir else None
    tickets_df = load_clean_tickets(data_dir=data_dir)
    print(f"Loaded {len(tickets_df):,} unique tickets for Step 4 classification.")

    # 2. Build Classifier Service
    client = build_llm_client(provider=args.provider, model_name=args.model)
    cache = ClassificationCache()
    service = ClassifierService(llm_client=client, cache=cache)

    # 3. Classify Batch
    classified_df = classify_tickets_batch(
        tickets_df=tickets_df,
        service=service,
        limit=args.limit,
        output_csv_path=args.output,
        bypass_cache=args.bypass_cache,
    )

    # 4. Print Summary & Quality Checks
    print_classification_summary(classified_df, tickets_df)


if __name__ == "__main__":
    main()
