"""Immutable domain entities shared across layers."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ScanStatus(str, Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_ERRORS = "COMPLETED_WITH_ERRORS"


class SourceType(str, Enum):
    FRAMEWORK = "FRAMEWORK"
    CATALOGUE = "CATALOGUE"
    INDEX = "INDEX"
    TREND = "TREND"
    ARTICLE = "ARTICLE"


class SourceRole(str, Enum):
    PRIMARY_DISCOVERY = "PRIMARY_DISCOVERY"
    SUPPORTING_DISCOVERY = "SUPPORTING_DISCOVERY"
    TREND_VALIDATION = "TREND_VALIDATION"


class SourceFamily(str, Enum):
    PROFESSIONAL_BODY = "PROFESSIONAL_BODY"
    HIGHER_LEARNING = "HIGHER_LEARNING"
    GOVERNMENT_AGENCY = "GOVERNMENT_AGENCY"


class EvidenceType(str, Enum):
    EXPLICIT_COMPETENCY = "EXPLICIT_COMPETENCY"
    COURSE = "COURSE"
    CERTIFICATION = "CERTIFICATION"
    RESEARCH_CAPABILITY = "RESEARCH_CAPABILITY"
    TECHNOLOGY_TOPIC = "TECHNOLOGY_TOPIC"
    TREND_SIGNAL = "TREND_SIGNAL"
    ARTICLE_TEXT = "ARTICLE_TEXT"
    PROFESSIONAL_RESOURCE = "PROFESSIONAL_RESOURCE"


@dataclass(frozen=True)
class Source:
    id: int | None
    name: str
    url: str
    organisation: str
    country: str = ""
    enabled: bool = True
    category: str = "Uncategorised"
    max_articles_per_scan: int = 25
    article_url_pattern: str = ""
    is_active: bool = True
    max_listing_pages: int = 3
    use_browser_rendering: bool = False
    evidence_label: str = "news / commentary"
    source_type: SourceType = SourceType.ARTICLE
    source_role: SourceRole = SourceRole.PRIMARY_DISCOVERY
    llm_allowed: bool = True
    source_family: SourceFamily = SourceFamily.PROFESSIONAL_BODY


@dataclass(frozen=True)
class ScanRun:
    id: int | None
    started_at: datetime
    completed_at: datetime | None
    status: ScanStatus
    error_summary: str | None = None
    sources_snapshot: tuple[dict, ...] = ()


@dataclass(frozen=True)
class SourceHealth:
    """Read model summarising a configured source's collected evidence."""
    source_id: int
    evidence_count: int
    last_evidence_at: datetime | None


@dataclass(frozen=True)
class FrameworkVersion:
    id: int | None
    version: str
    created_at: datetime
    is_current: bool


@dataclass(frozen=True)
class SubFunctionalArea:
    id: int | None
    framework_version_id: int
    cap_area: str | None
    name: str
    description: str | None


@dataclass(frozen=True)
class Competency:
    id: int | None
    sub_functional_area_id: int
    name: str
    description: str


@dataclass(frozen=True)
class Evidence:
    id: int | None
    scan_run_id: int
    source_id: int
    evidence_type: str
    title: str
    publication_date: str | None
    organisation: str
    url: str
    article_text: str
    extracted_at: datetime
    explicit_or_inferred: str = "INFERRED"


@dataclass(frozen=True)
class RecommendationBatch:
    id: int | None
    framework_version_id: int
    scan_run_id: int | None
    created_at: datetime
    framework_snapshot: str = "{}"


@dataclass(frozen=True)
class Recommendation:
    id: int | None
    batch_id: int
    recommendation_type: str
    confidence: float
    reasoning: str
    sub_functional_area: str = ""
    competency: str = ""
    kind_of_changes_suggested: str = ""
    reasons_for_suggesting_the_changes: str = ""
    supporting_evidence_ids: tuple[int, ...] = ()
    supporting_urls: tuple[str, ...] = ()
    supporting_organisations: tuple[str, ...] = ()


@dataclass(frozen=True)
class FallbackRecovery:
    id: int | None
    scan_run_id: int | None
    source_name: str
    organisation: str
    source_url: str
    recovery_status: str
    recovered_item_count: int
    raw_result: str
    created_at: datetime
