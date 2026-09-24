from datetime import datetime

from src.models.domain import Evidence
from src.services.evidence_organiser import EvidenceOrganiser


def _evidence(evidence_id: int, organisation: str, evidence_type: str, title: str = "Evidence") -> Evidence:
    return Evidence(
        evidence_id,
        1,
        1,
        evidence_type,
        title,
        None,
        organisation,
        f"https://example.org/{organisation.lower().replace(' ', '-')}/{evidence_id}",
        "This source discusses systems engineering, AI governance, digital engineering, training, standards, and STE workforce capabilities. " * 5,
        datetime.now(),
        "EXPLICIT" if evidence_type == "EXPLICIT_COMPETENCY" else "INFERRED",
    )


def test_evidence_organiser_groups_full_batch_by_organisation_and_evidence_class() -> None:
    """The LLM receives a full-batch organisation map, not only a flat first-N list."""
    evidence = [
        _evidence(1, "IET", "EXPLICIT_COMPETENCY", "Skills framework"),
        _evidence(2, "IET", "RESEARCH_CAPABILITY", "Skills survey"),
        _evidence(3, "MIT", "PROFESSIONAL_RESOURCE", "Course catalogue"),
        _evidence(4, "IEEE", "ARTICLE_TEXT", "AI signal"),
    ]

    organised = EvidenceOrganiser.build(evidence)

    assert organised["total_evidence_items"] == 4
    assert organised["quality_summary"]["label"] == "Structured-heavy"
    assert organised["quality_summary"]["primary_evidence_items"] == 3
    assert organised["quality_summary"]["signal_evidence_items"] == 1
    assert organised["quality_summary"]["primary_share"] == 0.75
    iet = next(item for item in organised["organisations"] if item["organisation"] == "IET")
    assert iet["counts"]["competencies_or_standards"] == 1
    assert iet["counts"]["research_reports_or_capability"] == 1
    mit = next(item for item in organised["organisations"] if item["organisation"] == "MIT")
    assert mit["counts"]["courses_programmes_or_resources"] == 1
    ieee = next(item for item in organised["organisations"] if item["organisation"] == "IEEE")
    assert ieee["counts"]["signals_and_topics"] == 1


def test_evidence_organiser_balances_detailed_selection_across_organisations() -> None:
    """Detailed evidence selection should not be monopolised by one organisation."""
    evidence = [
        _evidence(1, "Org A", "ARTICLE_TEXT"),
        _evidence(2, "Org A", "ARTICLE_TEXT"),
        _evidence(3, "Org B", "EXPLICIT_COMPETENCY"),
        _evidence(4, "Org C", "PROFESSIONAL_RESOURCE"),
    ]

    selected = EvidenceOrganiser.select_for_detail(evidence, 3)

    assert {item.organisation for item in selected} == {"Org A", "Org B", "Org C"}
    assert selected[0].organisation == "Org A"


def test_evidence_organiser_flags_signal_heavy_batches() -> None:
    """The organised scan tells officers when evidence is mostly trend/signal material."""
    evidence = [
        _evidence(1, "Org A", "ARTICLE_TEXT"),
        _evidence(2, "Org A", "TREND_SIGNAL"),
        _evidence(3, "Org B", "TECHNOLOGY_TOPIC"),
        _evidence(4, "Org C", "COURSE"),
    ]

    organised = EvidenceOrganiser.build(evidence)

    assert organised["quality_summary"]["label"] == "Signal-heavy"
    assert organised["quality_summary"]["signal_share"] == 0.75
