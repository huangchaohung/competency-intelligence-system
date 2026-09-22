"""Recommendation creation application service."""
from datetime import datetime
from src.core.exceptions import RecommendationError
from src.llm.competency_analyst import CompetencyAnalyst, RecommendationDraft, MAX_CHARS_PER_EVIDENCE, MAX_EVIDENCE_ITEMS, MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION
from src.models.domain import Evidence, FrameworkVersion, Recommendation
from src.services.evidence_organiser import EvidenceOrganiser
from src.services.operational_logger import NullOperationalLogger, OperationalLogger
from src.repositories.recommendation_repository import RecommendationRepository


class RecommendationService:
    """Create traceable recommendation batches from validated analyst output."""
    def __init__(self, repository: RecommendationRepository, analyst: CompetencyAnalyst, operational_logger: OperationalLogger | NullOperationalLogger | None = None) -> None:
        self._repository = repository
        self._analyst = analyst
        self._operational_logger = operational_logger or NullOperationalLogger()

    def generate(self, framework: FrameworkVersion, framework_data: dict, evidence: list[Evidence], scan_run_id: int | None = None) -> list[Recommendation]:
        """Persist a validated recommendation batch for supplied evidence."""
        if not evidence:
            raise RecommendationError("At least one evidence item is required")
        selected_evidence = EvidenceOrganiser.select_for_detail(evidence, MAX_EVIDENCE_ITEMS)
        organised_scan = EvidenceOrganiser.build(evidence)
        self._operational_logger.event(
            "recommendation_generation_started",
            {
                "framework_version_id": framework.id,
                "framework_version": framework.version,
                "scan_run_id": scan_run_id,
                "evidence_count": len(evidence),
                "selected_evidence_count": len(selected_evidence),
                "organised_scan_quality": organised_scan.get("quality_summary", {}),
            },
        )
        evidence_data = {
            "organised_scan": organised_scan,
            "selected_evidence": [
                {
                    "id": item.id,
                    "title": item.title,
                    "organisation": item.organisation,
                    "url": item.url,
                    "evidence_type": item.evidence_type,
                    "explicit_or_inferred": item.explicit_or_inferred,
                    "article_text": item.article_text[:MAX_CHARS_PER_EVIDENCE],
                }
                for item in selected_evidence
            ],
        }
        drafts = self._analyst.analyse(framework_data, evidence_data)
        evidence_by_id = {item.id: item for item in evidence if item.id is not None}
        canonical_support = [self._canonicalise_support(draft, evidence_by_id) for draft in drafts]
        batch = self._repository.create_batch(framework.id or 0, datetime.now().astimezone(), scan_run_id, framework_data)
        recommendations = [
            self._repository.add(
                Recommendation(
                    None,
                    batch.id or 0,
                    draft.recommendation_type,
                    draft.confidence,
                    draft.reasoning,
                    draft.sub_functional_area,
                    draft.competency,
                    draft.kind_of_changes_suggested,
                    draft.reasons_for_suggesting_the_changes,
                    evidence_ids,
                    urls,
                    organisations,
                )
            )
            for draft, (evidence_ids, urls, organisations) in zip(drafts, canonical_support, strict=True)
        ]
        self._operational_logger.event(
            "recommendation_generation_completed",
            {
                "recommendation_batch_id": batch.id,
                "framework_version_id": framework.id,
                "scan_run_id": scan_run_id,
                "stored_recommendation_count": len(recommendations),
                "recommendation_types": [item.recommendation_type for item in recommendations],
            },
        )
        return recommendations

    def answer_question(self, context: dict, question: str) -> str:
        """Answer a follow-up question grounded in the supplied batch context."""
        if not question.strip():
            raise RecommendationError("A question is required")
        self._operational_logger.event("batch_question_started", {"question": question.strip()})
        return self._analyst.answer_question(context, question.strip())

    @staticmethod
    def _canonicalise_support(draft: RecommendationDraft, evidence_by_id: dict[int, Evidence]) -> tuple[tuple[int, ...], tuple[str, ...], tuple[str, ...]]:
        """Use cited evidence IDs as the single source of truth for provenance."""
        if not draft.supporting_evidence_ids:
            raise RecommendationError("Model response must cite at least one evidence ID")
        canonical_ids: list[int] = []
        canonical_urls: list[str] = []
        canonical_organisations: list[str] = []
        seen: set[int] = set()
        for evidence_id in draft.supporting_evidence_ids:
            if len(canonical_ids) >= MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION:
                break
            if evidence_id in seen:
                continue
            evidence = evidence_by_id.get(evidence_id)
            if evidence is None:
                raise RecommendationError("Model response references evidence outside this run")
            seen.add(evidence_id)
            canonical_ids.append(evidence_id)
            canonical_urls.append(evidence.url)
            canonical_organisations.append(evidence.organisation)
        return tuple(canonical_ids), tuple(canonical_urls), tuple(canonical_organisations)
