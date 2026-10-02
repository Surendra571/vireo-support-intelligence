"""Unit and integration tests for AI-assisted ticket classification component.
Tests schema validity, controlled taxonomy enforcement, caching, malformed JSON recovery,
retry mechanisms, error containment, and model interchangeability.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict
import pytest

from app.services.classifier import (
    ALLOWED_CUSTOMER_INTENTS,
    ALLOWED_PRIMARY_ISSUES,
    ALLOWED_REPEAT_SIGNALS,
    ALLOWED_RESOLUTION_TYPES,
    ALLOWED_ROOT_CAUSES,
    BaseLLMClient,
    ClassificationCache,
    ClassifierService,
    RuleBasedTaxonomyClient,
    compute_content_hash,
)


class MockFlakyLLMClient(BaseLLMClient):
    """Mock LLM client that fails N times before succeeding or always fails."""

    def __init__(self, fail_count: int = 1, success_payload: str = "{}"):
        self.fail_count = fail_count
        self.attempts = 0
        self.success_payload = success_payload

    @property
    def model_name(self) -> str:
        return "mock-flaky-client"

    def generate_json(self, prompt: str) -> str:
        self.attempts += 1
        if self.attempts <= self.fail_count:
            raise ConnectionError(f"Simulated network timeout on attempt {self.attempts}")
        return self.success_payload


class MockCustomLLMClient(BaseLLMClient):
    """Mock client verifying polymorphic model replacement without changing analytics layer."""

    @property
    def model_name(self) -> str:
        return "custom-enterprise-llm-v2"

    def generate_json(self, prompt: str) -> str:
        return json.dumps(
            {
                "primary_issue": "earbud_not_charging",
                "secondary_issue": None,
                "customer_intent": "request_replacement",
                "resolution_type": "replacement_approved",
                "repeat_contact_signal": "yes",
                "root_cause_signal": "hardware_component_fault",
                "confidence": 0.95,
            }
        )


@pytest.fixture
def temp_cache(tmp_path: Path) -> ClassificationCache:
    """Fixture providing an isolated SQLite cache in tmp_path."""
    db_file = tmp_path / "test_cache.sqlite"
    cache = ClassificationCache(db_path=db_file)
    yield cache
    cache.close()


@pytest.fixture
def classifier_service(temp_cache: ClassificationCache) -> ClassifierService:
    """Fixture providing ClassifierService with RuleBasedTaxonomyClient and temp cache."""
    return ClassifierService(
        llm_client=RuleBasedTaxonomyClient(),
        cache=temp_cache,
        prompt_path="prompts/classification_v1.txt",
        prompt_version="v1",
    )


# ==============================================================================
# 1. HASH DETERMINISM TESTS
# ==============================================================================
def test_compute_content_hash_determinism():
    """Verify hash is identical for identical content regardless of leading/trailing whitespace."""
    hash1 = compute_content_hash(
        customer_message="  earbud not working  ",
        agent_notes="replaced unit",
        channel="chat",
        product_sku="va-tws-01",
        category="Audio Quality",
        assigned_team="Tech Support",
    )
    hash2 = compute_content_hash(
        customer_message="earbud not working",
        agent_notes="replaced unit",
        channel="CHAT",
        product_sku="VA-TWS-01",
        category="audio quality",
        assigned_team="tech support",
    )
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex string


def test_compute_content_hash_sensitivity():
    """Verify hash changes when ticket content changes."""
    hash1 = compute_content_hash(
        customer_message="battery drains fast",
        agent_notes="reset done",
        channel="chat",
        product_sku="SKU1",
        category="Battery",
        assigned_team="Team A",
    )
    hash2 = compute_content_hash(
        customer_message="bluetooth pairing fails",
        agent_notes="reset done",
        channel="chat",
        product_sku="SKU1",
        category="Battery",
        assigned_team="Team A",
    )
    assert hash1 != hash2


# ==============================================================================
# 2. CACHE STORAGE & RETRIEVAL TESTS
# ==============================================================================
def test_classification_cache_put_and_get(temp_cache: ClassificationCache):
    """Verify cache properly stores and returns structured classification."""
    ticket_id = "TK-TEST-001"
    content_hash = "abc123hash"
    classification = {
        "primary_issue": "delivery_delayed_not_received",
        "secondary_issue": None,
        "customer_intent": "request_delivery_status",
        "resolution_type": "inquiry_answered_info_shared",
        "repeat_contact_signal": "unclear",
        "root_cause_signal": "carrier_logistics_failure",
        "confidence": 0.88,
    }

    # Verify initially absent
    assert temp_cache.get(ticket_id, content_hash) is None

    # Put into cache
    temp_cache.put(
        ticket_id=ticket_id,
        content_hash=content_hash,
        prompt_version="v1",
        model="test-model",
        classification=classification,
        raw_response=json.dumps(classification),
    )

    # Retrieve and verify
    cached = temp_cache.get(ticket_id, content_hash)
    assert cached is not None
    assert cached["primary_issue"] == "delivery_delayed_not_received"
    assert cached["customer_intent"] == "request_delivery_status"
    assert cached["confidence"] == 0.88
    assert cached["_metadata"]["cached"] is True
    assert cached["_metadata"]["model"] == "test-model"
    assert cached["_metadata"]["prompt_version"] == "v1"


def test_cache_miss_on_different_content_hash(temp_cache: ClassificationCache):
    """Verify cache returns None when ticket_id matches but content has changed."""
    ticket_id = "TK-TEST-002"
    temp_cache.put(
        ticket_id=ticket_id,
        content_hash="hash_version_1",
        prompt_version="v1",
        model="test-model",
        classification={"primary_issue": "battery_drain_fast", "confidence": 0.8},
    )
    assert temp_cache.get(ticket_id, "hash_version_2") is None


# ==============================================================================
# 3. SCHEMA & TAXONOMY VALIDATION TESTS
# ==============================================================================
def test_sanitize_and_validate_strict_taxonomy(classifier_service: ClassifierService):
    """Verify that values outside controlled taxonomy are coerced to 'unknown' or 'unclear'."""
    invalid_payload = {
        "primary_issue": "made_up_issue_not_in_taxonomy",
        "secondary_issue": "another_invalid_issue",
        "customer_intent": "wants_free_food",
        "resolution_type": "magic_teleportation",
        "repeat_contact_signal": "maybe_sort_of",
        "root_cause_signal": "alien_interference",
        "confidence": "high",  # invalid float
    }
    validated = classifier_service._sanitize_and_validate(invalid_payload)

    assert validated["primary_issue"] == "unknown"
    assert validated["secondary_issue"] is None
    assert validated["customer_intent"] == "unknown"
    assert validated["resolution_type"] == "unknown"
    assert validated["repeat_contact_signal"] == "unclear"
    assert validated["root_cause_signal"] == "unknown"
    assert validated["confidence"] == 0.5


def test_taxonomy_constants_conformity():
    """Verify all defined categories conform to allowed lists."""
    assert "battery_drain_fast" in ALLOWED_PRIMARY_ISSUES
    assert "delivery_delayed_not_received" in ALLOWED_PRIMARY_ISSUES
    assert "request_replacement" in ALLOWED_CUSTOMER_INTENTS
    assert "troubleshooting_guided" in ALLOWED_RESOLUTION_TYPES
    assert "premature_ticket_closure" in ALLOWED_ROOT_CAUSES
    assert set(ALLOWED_REPEAT_SIGNALS) == {"yes", "no", "unclear"}


# ==============================================================================
# 4. JSON REPAIR & CLEANUP TESTS
# ==============================================================================
def test_clean_and_repair_json(classifier_service: ClassifierService):
    """Verify cleaning markdown fences, preambles, and trailing commas."""
    markdown_wrapped = """```json
    {
      "primary_issue": "bluetooth_pairing_failed",
      "customer_intent": "request_technical_support",
      "confidence": 0.85,
    }
    ```"""
    repaired = classifier_service._clean_and_repair_json(markdown_wrapped)
    assert repaired["primary_issue"] == "bluetooth_pairing_failed"
    assert repaired["customer_intent"] == "request_technical_support"
    assert repaired["confidence"] == 0.85


# ==============================================================================
# 5. RETRY & FAILURE CONTAINMENT TESTS
# ==============================================================================
def test_retry_on_transient_failure(temp_cache: ClassificationCache):
    """Verify classifier retries on transient errors and succeeds when model recovers."""
    success_json = json.dumps(
        {
            "primary_issue": "app_crash_bug",
            "secondary_issue": None,
            "customer_intent": "request_technical_support",
            "resolution_type": "troubleshooting_guided",
            "repeat_contact_signal": "unclear",
            "root_cause_signal": "firmware_software_bug",
            "confidence": 0.9,
        }
    )
    flaky_client = MockFlakyLLMClient(fail_count=2, success_payload=success_json)
    service = ClassifierService(
        llm_client=flaky_client,
        cache=temp_cache,
        max_retries=3,
        base_delay=0.01,
    )

    ticket = {
        "ticket_id": "TK-RETRY-01",
        "customer_message": "Vireo app keeps crashing on launch",
        "agent_notes": "guided customer to reinstall app",
        "channel": "chat",
        "product_sku": "VA-TWS-01",
        "category": "App & Firmware",
        "assigned_team": "App Support",
    }
    result = service.classify_ticket(ticket)
    assert flaky_client.attempts == 3
    assert result["primary_issue"] == "app_crash_bug"
    assert result["confidence"] == 0.9


def test_failure_containment_never_breaks_batch(temp_cache: ClassificationCache):
    """Verify persistent LLM failure returns a structured fallback rather than crashing."""
    always_failing_client = MockFlakyLLMClient(fail_count=10)
    service = ClassifierService(
        llm_client=always_failing_client,
        cache=temp_cache,
        max_retries=2,
        base_delay=0.01,
    )

    ticket = {
        "ticket_id": "TK-FAIL-01",
        "customer_message": "some text",
        "agent_notes": "some note",
        "channel": "email",
        "product_sku": "VA-ANC-01",
        "category": "Other",
        "assigned_team": "Tier 1",
    }
    result = service.classify_ticket(ticket)

    assert result["primary_issue"] == "unknown"
    assert result["confidence"] == 0.0
    assert result["_metadata"]["cached"] is False
    assert "Simulated network timeout" in result["_metadata"]["error"]


# ==============================================================================
# 6. MODEL REPLACEMENT / INTERCHANGEABILITY TEST
# ==============================================================================
def test_pluggable_model_replacement(temp_cache: ClassificationCache):
    """Verify that any custom LLM client implementing BaseLLMClient works seamlessly."""
    custom_client = MockCustomLLMClient()
    service = ClassifierService(llm_client=custom_client, cache=temp_cache)

    ticket = {
        "ticket_id": "TK-CUSTOM-01",
        "customer_message": "Right earbud dead",
        "agent_notes": "RMA approved",
        "channel": "chat",
        "product_sku": "VA-TWS-01",
        "category": "Audio Quality",
        "assigned_team": "Hardware",
    }
    result = service.classify_ticket(ticket)

    assert result["_metadata"]["model"] == "custom-enterprise-llm-v2"
    assert result["primary_issue"] == "earbud_not_charging"
    assert result["customer_intent"] == "request_replacement"
    assert result["resolution_type"] == "replacement_approved"
    assert result["repeat_contact_signal"] == "yes"
    assert result["confidence"] == 0.95


# ==============================================================================
# 7. END-TO-END CLASSIFIER SERVICE ACCURACY TEST
# ==============================================================================
def test_end_to_end_classification_scenarios(classifier_service: ClassifierService):
    """Test realistic support ticket scenarios covering primary issue, intent, and repeat signals."""
    # Scenario A: Delivery Delay
    ticket_a = {
        "ticket_id": "TK-A",
        "customer_message": "My order has not been delivered yet, tracking is stuck for 5 days",
        "agent_notes": "Advised cx to wait 24h, updated tracking link",
        "channel": "chat",
        "product_sku": "VA-TWS-01",
        "category": "Delivery & Shipping",
        "assigned_team": "Logistics",
    }
    res_a = classifier_service.classify_ticket(ticket_a, bypass_cache=True)
    assert res_a["primary_issue"] == "delivery_delayed_not_received"
    assert res_a["customer_intent"] == "request_delivery_status"
    assert res_a["root_cause_signal"] == "carrier_logistics_failure"
    assert res_a["resolution_type"] == "inquiry_answered_info_shared"

    # Scenario B: Explicit Repeat Contact & Premature Closure
    ticket_b = {
        "ticket_id": "TK-B",
        "customer_message": "I already told your colleague this 2 weeks ago! Battery drains in 30 mins. Send replacement.",
        "agent_notes": "RMA initiated. rplc dispatched.",
        "channel": "email",
        "product_sku": "VA-ANC-01",
        "category": "Charging & Battery",
        "assigned_team": "Audio Hardware",
    }
    res_b = classifier_service.classify_ticket(ticket_b, bypass_cache=True)
    assert res_b["primary_issue"] == "battery_drain_fast"
    assert res_b["customer_intent"] == "request_replacement"
    assert res_b["repeat_contact_signal"] == "yes"
    assert res_b["root_cause_signal"] == "premature_ticket_closure"
    assert res_b["resolution_type"] == "replacement_approved"

    # Scenario C: Payment debit failure
    ticket_c = {
        "ticket_id": "TK-C",
        "customer_message": "Payment failed after money was debited from my account",
        "agent_notes": "ARN shared with cx. refund of rs 1499 initiated to source",
        "channel": "chat",
        "product_sku": "VA-TWS-01",
        "category": "Billing & Payments",
        "assigned_team": "Billing",
    }
    res_c = classifier_service.classify_ticket(ticket_c, bypass_cache=True)
    assert res_c["primary_issue"] == "payment_failed_debited"
    assert res_c["customer_intent"] == "request_invoice_billing"
    assert res_c["resolution_type"] == "refund_processed"
    assert res_c["root_cause_signal"] == "payment_gateway_sync_failure"
