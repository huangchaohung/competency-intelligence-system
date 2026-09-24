"""Tests for historical fallback recovery display/export helpers."""
import json
from datetime import datetime

from src.dashboard.scan_report import _fallback_recovery_export_payload, _fallback_recovery_item_rows, _fallback_recovery_summary_rows
from src.models.domain import FallbackRecovery


def test_fallback_recovery_history_rows_and_export_are_json_safe() -> None:
    """History can summarise and export saved LLM fallback recovery records."""
    recovery = FallbackRecovery(
        3,
        9,
        "Org A Catalogue",
        "Org A",
        "https://a.example/catalogue",
        "COMPLETED",
        1,
        json.dumps(
            {
                "recovered_items": [
                    {
                        "title": "AI engineering course",
                        "url": "https://a.example/course",
                        "evidence_class": "course_programme_or_resource",
                        "summary": "A course for AI engineering.",
                        "explicit_or_inferred": "EXPLICIT",
                        "confidence": 0.82,
                        "verification_status": "✅ Verified by URL",
                    }
                ],
                "source_maintenance_advice": {
                    "recommendation_type": "REPLACE_SOURCE_URL",
                    "recommended_replacement_urls": ["https://a.example/better-catalogue"],
                    "reason": "The replacement URL appears more direct.",
                    "confidence": 0.74,
                    "requires_officer_approval": True,
                },
                "verification_summary": {"✅ Verified by URL": 1},
                "recovery_notes": "Recovered one item.",
            }
        ),
        datetime.fromisoformat("2026-08-27T10:30:00+08:00"),
    )

    summary_rows = _fallback_recovery_summary_rows([recovery])
    item_rows = _fallback_recovery_item_rows(recovery)
    export_payload = _fallback_recovery_export_payload([recovery])

    assert summary_rows[0]["Record ID"] == 3
    assert summary_rows[0]["Recovered items"] == 1
    assert "Replace Source URL · 74%" in summary_rows[0]["Source advice"]
    assert "Reason: The replacement URL appears more direct." in summary_rows[0]["Source advice"]
    assert "Suggested URL(s): https://a.example/better-catalogue" in summary_rows[0]["Source advice"]
    assert summary_rows[0]["Provenance"] == "🤖 LLM assisted"
    assert summary_rows[0]["Verification"] == {"✅ Verified by URL": 1}
    assert item_rows[0]["Evidence class"] == "course programme or resource"
    assert item_rows[0]["Provenance"] == "🤖 LLM assisted"
    assert item_rows[0]["Verification"] == "✅ Verified by URL"
    assert item_rows[0]["Confidence"] == "82%"
    assert export_payload[0]["provenance"] == "🤖 LLM assisted"
    assert export_payload[0]["verification_status"] == {"✅ Verified by URL": 1}
    assert export_payload[0]["result"]["recovered_items"][0]["title"] == "AI engineering course"
    assert json.loads(json.dumps(export_payload))[0]["id"] == 3
