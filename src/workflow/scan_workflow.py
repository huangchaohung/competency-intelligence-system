"""End-to-end evidence scan orchestration."""
import logging
import re
from datetime import datetime
from typing import Callable
from urllib.parse import urlparse
from src.extractor.article_extractor import ArticleExtractor
from src.core.exceptions import CompetencyIntelligenceError, ScanError
from src.models.domain import ScanRun, ScanStatus
from src.repositories.scan_repository import ScanRepository
from src.repositories.source_repository import SourceRepository
from src.scanner.source_router import SourceRouter
from src.scanner.web_page_scanner import WebPageScanner
from src.services.operational_logger import NullOperationalLogger, OperationalLogger

LOGGER = logging.getLogger(__name__)


class ScanWorkflow:
    """Run all enabled source scans independently."""
    EVIDENCE_RETENTION_RUNS = 5

    def __init__(self, sources: SourceRepository, scans: ScanRepository, scanner: WebPageScanner, extractor: ArticleExtractor, operational_logger: OperationalLogger | NullOperationalLogger | None = None) -> None:
        self._sources, self._scans, self._scanner, self._extractor = sources, scans, scanner, extractor
        self._router = SourceRouter(scanner)
        self._operational_logger = operational_logger or NullOperationalLogger()

    def run(self, progress_callback: Callable[[int, int, str, str, str, str], None] | None = None) -> ScanRun:
        """Store clean evidence from every source and return the completed run."""
        enabled_sources = self._sources.list_enabled()
        sources_snapshot = [self._source_snapshot(source) for source in enabled_sources]
        run = self._scans.create_run(datetime.now().astimezone(), sources_snapshot)
        self._operational_logger.event(
            "scan_started",
            {
                "scan_run_id": run.id,
                "enabled_source_count": len(enabled_sources),
                "sources_snapshot": sources_snapshot,
            },
        )
        errors: list[str] = []
        seen_urls: set[str] = set()
        stored_urls: set[str] = set()
        total_sources = len(enabled_sources)
        for index, source in enumerate(enabled_sources, start=1):
            source_started_at = datetime.now().astimezone()
            source_stats = {
                "scan_run_id": run.id,
                "source_id": source.id,
                "source_name": source.name,
                "organisation": source.organisation,
                "source_url": source.url,
                "source_family": source.source_family.value,
                "source_type": source.source_type.value,
                "source_role": source.source_role.value,
                "country": source.country,
                "use_browser_rendering": source.use_browser_rendering,
                "max_articles_per_scan": source.max_articles_per_scan,
                "max_listing_pages": source.max_listing_pages,
                "discovered_url_count": 0,
                "stored_evidence_count": 0,
                "skipped_utility_count": 0,
                "skipped_duplicate_count": 0,
                "skipped_out_of_scope_count": 0,
                "skipped_extraction_error_count": 0,
            }
            self._operational_logger.event("source_scan_started", source_stats)
            if progress_callback:
                progress_callback(index, total_sources, source.name, source.source_family.value, source.source_type.value, "start")
            try:
                discovered_urls = self._router.discover(source)
                source_stats["discovered_url_count"] = len(discovered_urls)
                self._operational_logger.event("source_urls_discovered", source_stats)
                if progress_callback:
                    progress_callback(index, total_sources, source.name, source.source_family.value, source.source_type.value, "discovered")
                for url in discovered_urls:
                    if self._is_utility_url(url):
                        LOGGER.info("Skipping utility URL '%s' from '%s'", url, source.name)
                        source_stats["skipped_utility_count"] += 1
                        continue
                    if url in seen_urls:
                        source_stats["skipped_duplicate_count"] += 1
                        continue
                    seen_urls.add(url)
                    try:
                        from src.scanner.nus_curriculum import matches as is_nus_curriculum, fetch_curriculum
                        if source.use_browser_rendering and is_nus_curriculum(url):
                            page = fetch_curriculum(self._scanner, url)
                        else:
                            page = self._scanner.fetch_url(url, source.name)
                        if page.url in stored_urls:
                            source_stats["skipped_duplicate_count"] += 1
                            continue
                        if self._is_utility_url(page.url):
                            LOGGER.info("Skipping utility redirect '%s' from '%s'", page.url, source.name)
                            source_stats["skipped_utility_count"] += 1
                            continue
                        evidence = self._extractor.extract(page, source, run.id or 0)
                        if self._is_utility_url(evidence.url):
                            LOGGER.info("Skipping utility evidence '%s' from '%s'", evidence.url, source.name)
                            source_stats["skipped_utility_count"] += 1
                            continue
                        if not self._matches_source_scope(evidence.url, source.url, source.article_url_pattern):
                            LOGGER.info("Skipping out-of-scope evidence '%s' from '%s'", evidence.url, source.name)
                            source_stats["skipped_out_of_scope_count"] += 1
                            continue
                    except CompetencyIntelligenceError as error:
                        LOGGER.info("Skipping article '%s' from '%s': %s", url, source.name, error)
                        source_stats["skipped_extraction_error_count"] += 1
                        continue
                    if evidence.url in stored_urls:
                        source_stats["skipped_duplicate_count"] += 1
                        continue
                    self._scans.add_evidence(evidence)
                    stored_urls.add(evidence.url)
                    source_stats["stored_evidence_count"] += 1
                if progress_callback:
                    progress_callback(index, total_sources, source.name, source.source_family.value, source.source_type.value, "done")
                source_stats["duration_seconds"] = (datetime.now().astimezone() - source_started_at).total_seconds()
                self._operational_logger.event("source_scan_completed", source_stats)
            except CompetencyIntelligenceError as error:
                LOGGER.warning("Source '%s' failed: %s", source.name, error)
                errors.append(f"{source.name}: {error}")
                source_stats["error"] = str(error)
                source_stats["duration_seconds"] = (datetime.now().astimezone() - source_started_at).total_seconds()
                self._operational_logger.event("source_scan_failed", source_stats)
                if progress_callback:
                    progress_callback(index, total_sources, source.name, source.source_family.value, source.source_type.value, "error")
        status = ScanStatus.COMPLETED_WITH_ERRORS if errors else ScanStatus.COMPLETED
        completed_run = self._scans.complete_run(run, status, "; ".join(errors) or None)
        pruned_count = self._scans.prune_evidence_to_recent_runs(self.EVIDENCE_RETENTION_RUNS)
        self._operational_logger.event(
            "scan_completed",
            {
                "scan_run_id": completed_run.id,
                "status": completed_run.status.value,
                "started_at": completed_run.started_at.isoformat(),
                "completed_at": completed_run.completed_at.isoformat() if completed_run.completed_at else None,
                "error_summary": completed_run.error_summary,
                "error_count": len(errors),
                "retention_runs": self.EVIDENCE_RETENTION_RUNS,
                "pruned_evidence_count": pruned_count,
            },
        )
        return completed_run

    @staticmethod
    def _source_snapshot(source) -> dict:
        """Return the source metadata stored with each scan batch."""
        return {
            "id": source.id,
            "name": source.name,
            "url": source.url,
            "organisation": source.organisation,
            "source_family": source.source_family.value,
            "source_type": source.source_type.value,
            "source_role": source.source_role.value,
            "llm_allowed": source.llm_allowed,
            "max_articles_per_scan": source.max_articles_per_scan,
            "max_listing_pages": source.max_listing_pages,
            "article_url_pattern": source.article_url_pattern,
            "use_browser_rendering": source.use_browser_rendering,
        }

    @staticmethod
    def _matches_source_scope(evidence_url: str, source_url: str, configured_pattern: str) -> bool:
        """Return whether final evidence URL remains inside configured source-specific scope."""
        pattern = configured_pattern or ScanWorkflow._default_article_pattern(source_url)
        if not pattern:
            return True
        try:
            compiled = re.compile(pattern)
        except re.error:
            return True
        return bool(compiled.search(urlparse(evidence_url).path))

    @staticmethod
    def _default_article_pattern(source_url: str) -> str:
        """Fallback source constraints for known brittle listing hubs."""
        url = source_url.lower()
        if "tech.gov.sg/media" in url:
            return r"^/media/.+"
        if "tech.gov.sg/technews" in url:
            return r"^/technews/.+"
        if "theiet.org/impact-society/policy-and-public-affairs/education-and-skills-policy/reports-and-papers/uk-skills-surveys" in url:
            return r"^/impact-society/policy-and-public-affairs/education-and-skills-policy/reports-and-papers/uk-skills-surveys(?:/.*)?$"
        if "asme.org/codes-standards" in url:
            return r"^/codes-standards(?:/.*)?$"
        return ""

    @staticmethod
    def _is_utility_url(url: str) -> bool:
        """Return whether a discovered URL is navigation/utility content, not evidence."""
        parsed = urlparse(url)
        value = url.lower()
        path = parsed.path.lower().rstrip("/")
        # Reviewed official training landing page, not general About navigation.
        if (parsed.scheme == 'https' and parsed.hostname == 'www.istructe.org'
                and path == '/about-us/what-we-do/events-and-training' and not parsed.query):
            return False
        if parsed.query:
            query = parsed.query.lower()
            if (
                query.startswith("page=")
                or "&page=" in query
                or query.startswith("f%5b")
                or "&f%5b" in query
                or query.startswith("year=")
                or "&year=" in query
                or query.startswith("category=")
                or "&category=" in query
                or query.startswith("ucam-ref=")
                or "&ucam-ref=" in query
            ):
                return True
        blocked_markers = (
            "javascript:", "mailto:", "tel:", "[resource:", "/cdn-cgi/", "/email-protection",
            "facebook.com/", "twitter.com/", "x.com/", "linkedin.com/", "instagram.com/", "youtube.com/", "tiktok.com/",
            "void(0)", "customised-programmess",
        )
        blocked_paths = (
            "/contact", "/contact-us", "/careers", "/jobs", "/membership", "/login", "/register",
            "/privacy", "/terms", "/sitemap", "/newsletter", "/newsletters", "/subscribe", "/about-us", "/about",
            "/legal", "/form", "/facebook", "/twitter", "/linkedin", "/instagram", "/youtube", "/tiktok",
        )
        blocked_path_markers = ("newsletter", "/taxonomy/", "/st/ppid-info")
        blocked_path_segments = (
            "about", "about-us", "careers", "contact", "contact-us", "jobs", "legal",
            "login", "membership", "privacy", "register", "sitemap", "subscribe", "terms",
        )
        path_segments = {segment for segment in path.split("/") if segment}
        return (
            any(marker in value for marker in blocked_markers)
            or any(blocked == path or path.startswith(f"{blocked}/") for blocked in blocked_paths)
            or any(marker in path for marker in blocked_path_markers)
            or any(segment == blocked or segment.startswith(f"{blocked}-") for segment in path_segments for blocked in blocked_path_segments)
        )
