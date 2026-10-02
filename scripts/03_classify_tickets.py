"""Vireo Audio Support Intelligence - Batch Ticket Classification Script
Executes structured AI classification on tickets with persistent caching,
retry handling, and controlled taxonomy validation.
Produces outputs/classified_tickets.csv.
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
    BaseLLMClient,
    ClassificationCache,
    ClassifierService,
    GeminiLLMClient,
    OpenAILLMClient,
    RuleBasedTaxonomyClient,
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
    progress_interval: int = 500,
) -> pd.DataFrame:
    """Classifies a batch of tickets and saves the results to CSV."""
    df_to_process = tickets_df.head(limit) if limit else tickets_df
    total_count = len(df_to_process)

    print(f"Starting classification on {total_count:,} tickets using model: '{service.llm_client.model_name}'...")
    start_time = time.time()

    records = []
    cache_hits = 0

    for idx, (_, row) in enumerate(df_to_process.iterrows(), 1):
        ticket_dict = {
            "ticket_id": row.get("ticket_id"),
            "channel": row.get("channel"),
            "product_sku": row.get("product_sku"),
            "category": row.get("category"),
            "assigned_team": row.get("assigned_team"),
            "customer_message": row.get("customer_message"),
            "agent_notes": row.get("agent_notes"),
        }

        classification = service.classify_ticket(ticket_dict)
        meta = classification.get("_metadata", {})
        if meta.get("cached", False):
            cache_hits += 1

        record = {
            "ticket_id": row.get("ticket_id"),
            "channel": row.get("channel"),
            "product_sku": row.get("product_sku"),
            "category": row.get("category"),
            "assigned_team": row.get("assigned_team"),
            "customer_message": row.get("customer_message"),
            "agent_notes": row.get("agent_notes"),
            "primary_issue": classification.get("primary_issue"),
            "secondary_issue": classification.get("secondary_issue"),
            "customer_intent": classification.get("customer_intent"),
            "resolution_type": classification.get("resolution_type"),
            "repeat_contact_signal": classification.get("repeat_contact_signal"),
            "root_cause_signal": classification.get("root_cause_signal"),
            "confidence": classification.get("confidence"),
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


def print_classification_summary(classified_df: pd.DataFrame) -> None:
    """Prints a clean summary of the classification results."""
    total = len(classified_df)
    avg_conf = round(float(classified_df["confidence"].mean()), 3)

    print("\n" + "=" * 80)
    print(" VIREO AUDIO AI TICKET CLASSIFICATION SUMMARY")
    print("=" * 80)
    print(f"Total Classified Tickets: {total:,}")
    print(f"Average Model Confidence: {avg_conf}")
    print(f"Model Identifier        : {classified_df['model'].iloc[0] if total > 0 else 'N/A'}")
    print(f"Prompt Version          : {classified_df['prompt_version'].iloc[0] if total > 0 else 'N/A'}")
    print("-" * 80)

    print("TOP 5 PRIMARY ISSUES:")
    for issue, cnt in classified_df["primary_issue"].value_counts().head(5).items():
        print(f"  * {issue:<32}: {cnt:>5,} ({(cnt/total*100):>5.1f}%)")

    print("\nCUSTOMER INTENTS:")
    for intent, cnt in classified_df["customer_intent"].value_counts().items():
        print(f"  * {intent:<32}: {cnt:>5,} ({(cnt/total*100):>5.1f}%)")

    print("\nRESOLUTION TYPES:")
    for res, cnt in classified_df["resolution_type"].value_counts().head(5).items():
        print(f"  * {res:<32}: {cnt:>5,} ({(cnt/total*100):>5.1f}%)")

    print("\nREPEAT CONTACT SIGNALS:")
    for sig, cnt in classified_df["repeat_contact_signal"].value_counts().items():
        print(f"  * {sig:<32}: {cnt:>5,} ({(cnt/total*100):>5.1f}%)")

    print("\nROOT CAUSE SIGNALS:")
    for rc, cnt in classified_df["root_cause_signal"].value_counts().head(5).items():
        print(f"  * {rc:<32}: {cnt:>5,} ({(cnt/total*100):>5.1f}%)")

    print("=" * 80 + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify Vireo Audio support tickets using AI with strict taxonomy and caching."
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="auto",
        choices=["auto", "gemini", "openai", "rule_based"],
        help="LLM provider to use (default: auto).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name (e.g. gemini-2.5-flash, gpt-4o-mini, vireo-semantic-classifier-v1).",
    )
    parser.add_argument(
        "--sample",
        type=str,
        default="all",
        help="Number of tickets to classify (e.g. '500', '1000', or 'all' [default: 'all']).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="outputs/classified_tickets.csv",
        help="Path for destination CSV output.",
    )
    parser.add_argument(
        "--cache-db",
        type=str,
        default="outputs/classification_cache.sqlite",
        help="Path to persistent SQLite cache database.",
    )
    parser.add_argument(
        "--prompt-path",
        type=str,
        default="prompts/classification_v1.txt",
        help="Path to versioned prompt template.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    tickets_df = load_clean_tickets()
    limit = None if args.sample.lower() == "all" else int(args.sample)

    llm_client = build_llm_client(args.provider, args.model)
    cache = ClassificationCache(db_path=args.cache_db)

    service = ClassifierService(
        llm_client=llm_client,
        cache=cache,
        prompt_path=args.prompt_path,
        prompt_version="v1",
    )

    classified_df = classify_tickets_batch(
        tickets_df=tickets_df,
        service=service,
        limit=limit,
        output_csv_path=args.output,
    )

    print_classification_summary(classified_df)


if __name__ == "__main__":
    main()
