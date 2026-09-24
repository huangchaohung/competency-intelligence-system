"""Tests for governed LLM fallback recovery parsing and prompt guardrails."""
import json

import pytest

from src.core.exceptions import RecommendationError
from src.llm.fallback_recovery import OpenAIFallbackRecoverer, fallback_recovery_result_payload, parse_fallback_recovery_response


def _source_maintenance_advice(replacement_urls=None) -> dict:
    return {
        "recommendation_type": "REPLACE_SOURCE_URL" if replacement_urls else "KEEP_CURRENT_SOURCE",
        "recommended_replacement_urls": replacement_urls or [],
        "reason": "Review the configured source URL based on fallback recovery.",
        "confidence": 0.7,
    }


def test_parse_fallback_recovery_response_accepts_valid_items() -> None:
    """Fallback recovery responses preserve source provenance and confidence."""
    result = parse_fallback_recovery_response(
        json.dumps(
            {
                "organisation": "Org A",
                "source_url": "https://a.example/catalogue",
                "recovered_items": [
                    {
                        "title": "Systems engineering competency framework",
                        "url": "https://a.example/framework",
                        "evidence_class": "competency_or_standard",
                        "summary": "Defines systems engineering capabilities for professional practice.",
                        "explicit_or_inferred": "EXPLICIT",
                        "confidence": 0.91,
                    }
                ],
                "source_maintenance_advice": _source_maintenance_advice(["https://a.example/better-catalogue"]),
                "recovery_notes": "Recovered one explicit framework item.",
            }
        )
    )

    assert result.organisation == "Org A"
    assert result.source_url == "https://a.example/catalogue"
    assert result.recovered_items[0].evidence_class == "competency_or_standard"
    assert result.recovered_items[0].confidence == 0.91
    assert result.source_maintenance_advice["recommendation_type"] == "REPLACE_SOURCE_URL"
    assert result.source_maintenance_advice["recommended_replacement_urls"] == ("https://a.example/better-catalogue",)


def test_parse_fallback_recovery_response_rejects_invented_or_invalid_urls() -> None:
    """Recovered evidence must remain auditable through valid URLs."""
    with pytest.raises(RecommendationError, match="valid source URL"):
        parse_fallback_recovery_response(
            json.dumps(
                {
                    "organisation": "Org A",
                    "source_url": "not-a-url",
                    "recovered_items": [],
                    "source_maintenance_advice": _source_maintenance_advice(),
                    "recovery_notes": "No recovery.",
                }
            )
        )


def test_parse_fallback_recovery_response_rejects_unknown_evidence_class() -> None:
    """The recovery output must use the governed evidence classes only."""
    with pytest.raises(RecommendationError, match="invalid evidence class"):
        parse_fallback_recovery_response(
            json.dumps(
                {
                    "organisation": "Org A",
                    "source_url": "https://a.example",
                    "recovered_items": [
                        {
                            "title": "Unclear item",
                            "url": "https://a.example/item",
                            "evidence_class": "marketing_claim",
                            "summary": "This should not be accepted.",
                            "explicit_or_inferred": "INFERRED",
                            "confidence": 0.5,
                        }
                    ],
                    "source_maintenance_advice": _source_maintenance_advice(),
                    "recovery_notes": "Recovered one item.",
                }
            )
        )


def test_parse_fallback_recovery_response_rejects_invalid_replacement_urls() -> None:
    """Replacement URL advice must stay auditable through real HTTP(S) links."""
    with pytest.raises(RecommendationError, match="invalid replacement URL"):
        parse_fallback_recovery_response(
            json.dumps(
                {
                    "organisation": "Org A",
                    "source_url": "https://a.example",
                    "recovered_items": [],
                    "source_maintenance_advice": _source_maintenance_advice(["not-a-url"]),
                    "recovery_notes": "No recovered evidence.",
                }
            )
        )


def test_parse_fallback_recovery_response_rejects_empty_source_advice_reason() -> None:
    """Source-maintenance advice must explain why officers should consider the change."""
    advice = _source_maintenance_advice(["https://a.example/better-source"])
    advice["reason"] = " "

    with pytest.raises(RecommendationError, match="must include a reason"):
        parse_fallback_recovery_response(
            json.dumps(
                {
                    "organisation": "Org A",
                    "source_url": "https://a.example",
                    "recovered_items": [],
                    "source_maintenance_advice": advice,
                    "recovery_notes": "No recovered evidence.",
                }
            )
        )


def test_fallback_recovery_prompt_preserves_governance_constraints() -> None:
    """The executable fallback prompt keeps the preview guardrails."""
    payload = {
        "mode": "llm_fallback_recovery_preview",
        "source": {"organisation": "Org A", "name": "Org A Training", "url": "https://a.example/training"},
        "scan_health": {"status": "No evidence"},
        "constraints": ["Do not invent source URLs, organisations, courses, competencies, or standards."],
    }

    prompt = OpenAIFallbackRecoverer._build_prompt(payload)

    assert "explicitly approved LLM fallback recovery pass" in prompt
    assert "Do not invent source URLs" in prompt
    assert "Return only JSON" in prompt


def test_fallback_recovery_result_payload_is_json_safe() -> None:
    """Recovered fallback results can be displayed and downloaded from Streamlit."""
    result = parse_fallback_recovery_response(
        json.dumps(
            {
                "organisation": "Org A",
                "source_url": "https://a.example",
                "recovered_items": [
                    {
                        "title": "Training catalogue",
                        "url": "https://a.example/training",
                        "evidence_class": "course_programme_or_resource",
                        "summary": "Lists STE training resources.",
                        "explicit_or_inferred": "EXPLICIT",
                        "confidence": 0.8,
                    }
                ],
                "source_maintenance_advice": _source_maintenance_advice(["https://a.example/new-training"]),
                "recovery_notes": "One item recovered.",
            }
        )
    )

    payload = fallback_recovery_result_payload(result)

    assert payload["organisation"] == "Org A"
    assert payload["recovered_item_count"] == 1
    assert payload["recovered_items"][0]["title"] == "Training catalogue"
    assert payload["source_maintenance_advice"]["recommended_replacement_urls"] == ["https://a.example/new-training"]
    assert payload["source_maintenance_advice"]["requires_officer_approval"] is True
    assert json.loads(json.dumps(payload))["recovery_notes"] == "One item recovered."
