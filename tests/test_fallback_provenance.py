"""Tests for fallback provenance and verification labels."""
from __future__ import annotations

from src.services.fallback_provenance import fallback_provenance_label, fallback_verification_label


def test_fallback_provenance_label_marks_ai_assisted_material() -> None:
    """Fallback records should never look like ordinary crawler evidence."""
    assert fallback_provenance_label() == "🤖 LLM assisted"


def test_fallback_verification_label_flags_low_confidence_items() -> None:
    """Low confidence recovered items need a stronger warning label."""
    assert fallback_verification_label({"verification_status": "✅ Verified by URL", "confidence": 0.2}) == "✅ Verified by URL"
    assert fallback_verification_label({"confidence": 0.49}) == "🔴 Low confidence recovery"
    assert fallback_verification_label({"confidence": 0.5}) == "🟡 Needs verification"
