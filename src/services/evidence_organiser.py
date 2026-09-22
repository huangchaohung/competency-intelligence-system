"""Prepare scan evidence for competency-oriented LLM reasoning."""
from collections import defaultdict

from src.models.domain import Evidence


PRIMARY_TYPES = {"EXPLICIT_COMPETENCY", "PROFESSIONAL_RESOURCE", "COURSE", "CERTIFICATION", "RESEARCH_CAPABILITY"}
SIGNAL_TYPES = {"ARTICLE_TEXT", "TREND_SIGNAL", "TECHNOLOGY_TOPIC"}
TYPE_BUCKETS = {
    "EXPLICIT_COMPETENCY": "competencies_or_standards",
    "PROFESSIONAL_RESOURCE": "courses_programmes_or_resources",
    "COURSE": "courses_programmes_or_resources",
    "CERTIFICATION": "courses_programmes_or_resources",
    "RESEARCH_CAPABILITY": "research_reports_or_capability",
    "TECHNOLOGY_TOPIC": "signals_and_topics",
    "TREND_SIGNAL": "signals_and_topics",
    "ARTICLE_TEXT": "signals_and_topics",
}


class EvidenceOrganiser:
    """Convert a large evidence batch into a compact organisation-level map."""

    @staticmethod
    def build(evidence: list[Evidence], max_items_per_bucket: int = 6) -> dict:
        """Group all evidence into competency/course/report/signal buckets by organisation."""
        quality_summary = EvidenceOrganiser._quality_summary(evidence)
        grouped: dict[str, dict] = defaultdict(lambda: {
            "counts": {
                "competencies_or_standards": 0,
                "courses_programmes_or_resources": 0,
                "research_reports_or_capability": 0,
                "signals_and_topics": 0,
            },
            "competencies_or_standards": [],
            "courses_programmes_or_resources": [],
            "research_reports_or_capability": [],
            "signals_and_topics": [],
        })
        for item in evidence:
            organisation = item.organisation or "Unknown organisation"
            bucket = TYPE_BUCKETS.get(item.evidence_type, "signals_and_topics")
            grouped[organisation]["counts"][bucket] += 1
            if len(grouped[organisation][bucket]) < max_items_per_bucket:
                grouped[organisation][bucket].append(EvidenceOrganiser._summarise_item(item))

        organisations = []
        for organisation, payload in sorted(grouped.items()):
            organisations.append({
                "organisation": organisation,
                "counts": payload["counts"],
                "competencies_or_standards": payload["competencies_or_standards"],
                "courses_programmes_or_resources": payload["courses_programmes_or_resources"],
                "research_reports_or_capability": payload["research_reports_or_capability"],
                "signals_and_topics": payload["signals_and_topics"],
            })
        return {
            "total_evidence_items": len(evidence),
            "organisation_count": len(organisations),
            "quality_summary": quality_summary,
            "organisations": organisations,
            "interpretation_guidance": (
                "Use competencies_or_standards, courses_programmes_or_resources, and research_reports_or_capability "
                "as primary evidence when they are STE-relevant. Use signals_and_topics as corroborating or outlier "
                "evidence, not as the sole basis for a major competency recommendation."
            ),
        }

    @staticmethod
    def _quality_summary(evidence: list[Evidence]) -> dict:
        """Summarise whether the organised scan is primary-source heavy or signal-heavy."""
        total = len(evidence)
        primary_count = sum(1 for item in evidence if item.evidence_type in PRIMARY_TYPES)
        signal_count = sum(1 for item in evidence if item.evidence_type in SIGNAL_TYPES)
        other_count = max(0, total - primary_count - signal_count)
        primary_share = round(primary_count / total, 2) if total else 0.0
        signal_share = round(signal_count / total, 2) if total else 0.0
        if total == 0:
            label = "No retained evidence"
        elif primary_share >= 0.6:
            label = "Structured-heavy"
        elif signal_share >= 0.6:
            label = "Signal-heavy"
        else:
            label = "Mixed"
        return {
            "label": label,
            "primary_evidence_items": primary_count,
            "signal_evidence_items": signal_count,
            "other_evidence_items": other_count,
            "primary_share": primary_share,
            "signal_share": signal_share,
        }

    @staticmethod
    def select_for_detail(evidence: list[Evidence], max_items: int) -> list[Evidence]:
        """Select a balanced set of citation-ready evidence from the full batch."""
        priority = {
            "EXPLICIT_COMPETENCY": 0,
            "PROFESSIONAL_RESOURCE": 1,
            "COURSE": 1,
            "CERTIFICATION": 1,
            "RESEARCH_CAPABILITY": 2,
            "TECHNOLOGY_TOPIC": 3,
            "TREND_SIGNAL": 3,
            "ARTICLE_TEXT": 4,
        }
        selected: list[Evidence] = []
        seen_ids: set[int | None] = set()
        by_organisation: dict[str, list[Evidence]] = defaultdict(list)
        for item in evidence:
            by_organisation[item.organisation or "Unknown organisation"].append(item)
        for items in by_organisation.values():
            items.sort(key=lambda item: (priority.get(item.evidence_type, 9), item.title))

        while len(selected) < max_items:
            added_this_round = False
            for organisation in sorted(by_organisation):
                if len(selected) >= max_items:
                    break
                items = by_organisation[organisation]
                while items and items[0].id in seen_ids:
                    items.pop(0)
                if not items:
                    continue
                item = items.pop(0)
                selected.append(item)
                seen_ids.add(item.id)
                added_this_round = True
            if not added_this_round:
                break
        return selected

    @staticmethod
    def _summarise_item(item: Evidence) -> dict:
        text = " ".join((item.article_text or "").split())
        return {
            "id": item.id,
            "title": item.title,
            "url": item.url,
            "evidence_type": item.evidence_type,
            "explicit_or_inferred": item.explicit_or_inferred,
            "snippet": text[:350],
        }
