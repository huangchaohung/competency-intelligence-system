"""Recommendation process orchestration."""
from src.core.exceptions import RecommendationError
from src.models.domain import Competency, FrameworkVersion, SubFunctionalArea
from src.repositories.framework_repository import FrameworkRepository
from src.repositories.scan_repository import ScanRepository
from src.services.recommendation_service import RecommendationService

HIDDEN_RECOMMENDATION_TYPES = {"ALREADY_COVERED", "INSUFFICIENT_EVIDENCE"}


class RecommendationWorkflow:
    """Coordinate framework context, evidence, and the analyst."""
    def __init__(self, frameworks: FrameworkRepository, scans: ScanRepository, recommendations: RecommendationService) -> None:
        self._frameworks, self._scans, self._recommendations = frameworks, scans, recommendations

    def run(self, evidence_batch_id: int | None = None) -> int:
        """Generate recommendations for the current framework and one evidence batch."""
        framework = self._frameworks.get_current()
        if framework is None:
            raise RecommendationError("Import a current framework before generating recommendations")
        framework_data = self._serialise_framework(framework)
        scan_run_id = evidence_batch_id
        if scan_run_id is None:
            latest_runs = self._scans.list_runs(limit=1)
            scan_run_id = latest_runs[0].id if latest_runs and latest_runs[0].id is not None else None
        evidence = self._scans.list_evidence_for_run(scan_run_id) if scan_run_id is not None else self._scans.list_evidence()
        recommendations = self._recommendations.generate(framework, framework_data, evidence, scan_run_id)
        return sum(1 for item in recommendations if item.recommendation_type not in HIDDEN_RECOMMENDATION_TYPES)

    def _serialise_framework(self, framework: FrameworkVersion) -> dict:
        areas = self._frameworks.list_areas(framework.id or 0)
        return {"version": framework.version, "sub_functional_areas": [self._serialise_area(area) for area in areas]}

    def _serialise_area(self, area: SubFunctionalArea) -> dict:
        competencies = self._frameworks.list_competencies(area.id or 0)
        return {"cap_area": area.cap_area, "name": area.name, "description": area.description, "competencies": [self._serialise_competency(item) for item in competencies]}

    @staticmethod
    def _serialise_competency(competency: Competency) -> dict:
        return {"name": competency.name, "description": competency.description, "definition": competency.description}
