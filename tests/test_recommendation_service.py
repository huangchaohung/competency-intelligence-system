from datetime import datetime

import pytest

from src.core.exceptions import RecommendationError
from src.llm.competency_analyst import MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION, RecommendationDraft
from src.models.domain import Evidence
from src.services.recommendation_service import RecommendationService


def _evidence(evidence_id: int, organisation: str, url: str) -> Evidence:
    return Evidence(
        evidence_id,
        1,
        1,
        "EXPLICIT_COMPETENCY",
        "Evidence",
        None,
        organisation,
        url,
        "Evidence text",
        datetime.now(),
        "EXPLICIT",
    )


def _draft(evidence_ids: tuple[int, ...]) -> RecommendationDraft:
    return RecommendationDraft(
        "NEW_COMPETENCY",
        0.8,
        "Reasoning",
        "Area",
        "Competency",
        "Add competency",
        "Reasons",
        evidence_ids,
        ("https://wrong.example.org",),
        ("Wrong organisation",),
    )


def test_recommendation_support_is_canonicalised_from_evidence_ids() -> None:
    """Stored provenance should come from evidence records, not model-paired arrays."""
    evidence = {
        1: _evidence(1, "Correct organisation", "https://correct.example.org"),
        2: _evidence(2, "Second organisation", "https://second.example.org"),
    }

    evidence_ids, urls, organisations = RecommendationService._canonicalise_support(_draft((1, 2, 1)), evidence)

    assert evidence_ids == (1, 2)
    assert urls == ("https://correct.example.org", "https://second.example.org")
    assert organisations == ("Correct organisation", "Second organisation")


def test_recommendation_support_rejects_missing_evidence_ids() -> None:
    """A recommendation without evidence IDs cannot be audited safely."""
    with pytest.raises(RecommendationError, match="at least one evidence ID"):
        RecommendationService._canonicalise_support(_draft(()), {})


def test_recommendation_support_rejects_unknown_evidence_ids() -> None:
    """The model cannot cite evidence outside the current run."""
    with pytest.raises(RecommendationError, match="outside this run"):
        RecommendationService._canonicalise_support(_draft((99,)), {})


def test_recommendation_support_keeps_at_most_ten_sources() -> None:
    """Stored provenance remains reviewable even if a model cites too many items."""
    evidence = {
        evidence_id: _evidence(evidence_id, f"Org {evidence_id}", f"https://example.org/{evidence_id}")
        for evidence_id in range(1, 13)
    }

    evidence_ids, urls, organisations = RecommendationService._canonicalise_support(_draft(tuple(range(1, 13))), evidence)

    assert len(evidence_ids) == MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION
    assert len(urls) == MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION
    assert len(organisations) == MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION
    assert evidence_ids == tuple(range(1, 11))
