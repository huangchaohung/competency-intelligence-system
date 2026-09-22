"""Shared provenance labels for LLM-assisted fallback recovery records."""
from __future__ import annotations

from typing import Any


PROVENANCE_LLM_ASSISTED = "🤖 LLM assisted"
VERIFICATION_NEEDS_REVIEW = "🟡 Needs verification"
VERIFICATION_LOW_CONFIDENCE = "🔴 Low confidence recovery"


def fallback_provenance_label() -> str:
    """Return the officer-facing provenance label for fallback records."""
    return PROVENANCE_LLM_ASSISTED


def fallback_verification_label(item: dict[str, Any] | None = None) -> str:
    """Return an officer-facing verification label for a recovered fallback item."""
    item = item or {}
    if item.get("verification_status"):
        return str(item["verification_status"])
    confidence = item.get("confidence")
    if isinstance(confidence, (float, int)) and confidence < 0.5:
        return VERIFICATION_LOW_CONFIDENCE
    return VERIFICATION_NEEDS_REVIEW
