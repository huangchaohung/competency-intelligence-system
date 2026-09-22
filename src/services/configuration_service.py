"""Configuration loading and validation."""
from pathlib import Path
from urllib.parse import urlparse
import re
import yaml
from src.core.exceptions import ConfigurationError
from src.models.domain import Source, SourceFamily, SourceRole, SourceType


class ConfigurationService:
    """Load explicit public source configuration."""
    def __init__(self, configuration_path: Path) -> None:
        self._configuration_path = configuration_path

    def load_sources(self) -> list[Source]:
        """Return valid source definitions from YAML."""
        try:
            document = yaml.safe_load(self._configuration_path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError) as error:
            raise ConfigurationError(f"Unable to read source configuration: {error}") from error
        return self._load_sources_from_document(document)

    def load_sources_from_text(self, text: str) -> list[Source]:
        """Return valid source definitions from YAML text without saving it."""
        try:
            document = yaml.safe_load(text) or {}
        except yaml.YAMLError as error:
            raise ConfigurationError(f"Unable to parse source configuration: {error}") from error
        return self._load_sources_from_document(document)

    def _load_sources_from_document(self, document: dict) -> list[Source]:
        """Return source definitions from a parsed YAML document."""
        if not isinstance(document, dict):
            raise ConfigurationError("Source configuration must be a YAML object with a 'sources' list")
        sources = document.get("sources", [])
        if not isinstance(sources, list):
            raise ConfigurationError("'sources' must be a list")
        result: list[Source] = []
        for item in sources:
            if not isinstance(item, dict) or not all(item.get(key) for key in ("name", "url", "organisation")):
                raise ConfigurationError("Each source requires name, url, and organisation")
            parsed = urlparse(item["url"])
            if parsed.scheme != "https" or not parsed.netloc:
                raise ConfigurationError(f"Source URL must be HTTPS: {item['url']}")
            evidence_label = str(item.get("evidence_label") or self._default_evidence_label(item["name"], item["url"], item["organisation"]))
            source_type = SourceType(str(item.get("source_type") or self._default_source_type(evidence_label, item["name"], item["url"], item["organisation"])))
            source_role = SourceRole(str(item.get("source_role") or self._default_source_role(evidence_label, item["name"], item["url"], item["organisation"])))
            source_family = SourceFamily(str(item.get("source_family") or self._default_source_family(item["organisation"], item["url"])))
            llm_allowed = bool(item.get("llm_allowed", True))
            result.append(Source(None, item["name"], item["url"], item["organisation"], str(item.get("country") or self._default_country(item["organisation"], item["url"])), bool(item.get("enabled", True)), str(item.get("category", "Uncategorised")), int(item.get("max_articles_per_scan", 25)), str(item.get("article_url_pattern", "")), True, int(item.get("max_listing_pages", 3)), bool(item.get("use_browser_rendering", False)), evidence_label, source_type, source_role, llm_allowed, source_family))
        self._validate_sources(result)
        return result

    @staticmethod
    def _default_evidence_label(name: str, url: str, organisation: str) -> str:
        text = f"{name} {url} {organisation}".lower()
        if any(marker in text for marker in ("standards.ieee.org", "uk-skills-surveys", "codes and standards", "competency", "standard", "guideline", "certificate", "admission-to-the-practice")):
            return "standards / guidance"
        if any(marker in text for marker in ("press-release", "press releases", "media-relations", "news release", "announcement", "speeches", "agency-circulars")):
            return "press release / official notice"
        if any(marker in text for marker in ("reports-and-papers", "research", "report", "survey", "findings", "strategy", "policy", "insights")):
            return "research / report"
        if any(marker in text for marker in ("blog", "feature", "news", "media", "technews", "news-and-media", "innovates", "spectrum.ieee.org", "news.mit.edu", "news.nus.edu.sg", "cam.ac.uk/news", "news-and-insights")):
            return "news / commentary"
        if any(marker in text for marker in ("catalogue", "course", "training", "events")):
            return "catalogue / training"
        return "news / commentary"

    @staticmethod
    def _default_country(organisation: str, url: str) -> str:
        text = f"{organisation} {url}".lower()
        if any(marker in text for marker in ("singapore", "aisingapore", "govtech", "nus.edu.sg", "ntu.edu.sg", "ies.org.sg")):
            return "Singapore"
        if any(marker in text for marker in ("ieee", "mit.edu", "harvard.edu", "cam.ac.uk", "stanford.edu")):
            return "United States"
        if any(marker in text for marker in ("raeng", "engc.org.uk", "theiet.org", "engineerscanada.ca", "nspe.org", "asce.org", "asme.org", "isaca.org", "isa.org", "uk")):
            return "United Kingdom"
        if "engineersaustralia" in text:
            return "Australia"
        if "swe.org" in text:
            return "United States"
        return "Unknown"

    @staticmethod
    def _default_source_family(organisation: str, url: str) -> str:
        text = f"{organisation} {url}".lower()
        if any(marker in text for marker in ("govtech", "dsta", "dso", "astar", "imda", "skillsfuture", "wsg", "pub.gov.sg", "nparks", "nrf", "enterprise singapore", "nist", "nasa", "nsf", "darpa", "ukri", "dstl", "oecd", "worldbank", "world bank", "commission", "jrc", "agency")):
            return SourceFamily.GOVERNMENT_AGENCY.value
        if any(marker in text for marker in ("university", ".edu", "nus", "ntu", "smu", "sutd", "sit", "suss", "oxford", "cambridge", "harvard", "mit", "stanford", "berkeley")):
            return SourceFamily.HIGHER_LEARNING.value
        return SourceFamily.PROFESSIONAL_BODY.value

    @staticmethod
    def _default_source_type(evidence_label: str, name: str, url: str, organisation: str) -> str:
        text = f"{evidence_label} {name} {url} {organisation}".lower()
        if any(marker in text for marker in ("catalogue", "course", "training", "learning", "certificate", "programme")):
            return SourceType.CATALOGUE.value
        if any(marker in text for marker in ("standards / guidance", "competency", "framework", "standard", "guideline", "codes and standards", "uk-spec")):
            return SourceType.FRAMEWORK.value
        if any(marker in text for marker in ("research / report", "survey", "report", "research", "insights")):
            return SourceType.INDEX.value
        if any(marker in text for marker in ("news / commentary", "technews", "spectrum.ieee.org", "trend", "foresight")):
            return SourceType.TREND.value
        return SourceType.ARTICLE.value

    @staticmethod
    def _default_source_role(evidence_label: str, name: str, url: str, organisation: str) -> str:
        text = f"{evidence_label} {name} {url} {organisation}".lower()
        if any(marker in text for marker in ("news / commentary", "technews", "spectrum.ieee.org", "trend", "foresight")):
            return SourceRole.TREND_VALIDATION.value
        if any(marker in text for marker in ("press release", "official notice", "announcement", "media", "news-and-media", "circulars")):
            return SourceRole.SUPPORTING_DISCOVERY.value
        return SourceRole.PRIMARY_DISCOVERY.value

    def save_sources(self, sources: list[Source]) -> None:
        """Atomically persist validated source definitions to YAML."""
        self._validate_sources(sources)
        document = {"sources": [{"name": source.name, "url": source.url, "organisation": source.organisation, "source_family": source.source_family.value, "country": source.country, "source_type": source.source_type.value, "source_role": source.source_role.value, "llm_allowed": source.llm_allowed, "category": source.category, "evidence_label": source.evidence_label, "max_articles_per_scan": source.max_articles_per_scan, "article_url_pattern": source.article_url_pattern, "enabled": source.enabled, "max_listing_pages": source.max_listing_pages, "use_browser_rendering": source.use_browser_rendering} for source in sources if source.is_active]}
        temporary_path = self._configuration_path.with_suffix(".tmp")
        try:
            temporary_path.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8")
            temporary_path.replace(self._configuration_path)
        except OSError as error:
            raise ConfigurationError(f"Unable to save source configuration: {error}") from error

    def validate_sources(self, sources: list[Source]) -> None:
        """Validate a proposed catalogue without changing persisted state."""
        self._validate_sources(sources)

    def _validate_sources(self, sources: list[Source]) -> None:
        """Validate sources using the same rules applied during loading."""
        seen_urls: set[str] = set()
        for source in sources:
            if not source.name.strip() or not source.organisation.strip():
                raise ConfigurationError("Each source requires name and organisation")
            parsed = urlparse(source.url)
            if parsed.scheme != "https" or not parsed.netloc:
                raise ConfigurationError(f"Source URL must be HTTPS: {source.url}")
            if source.url in seen_urls:
                raise ConfigurationError(f"Source URL is duplicated: {source.url}")
            seen_urls.add(source.url)
            if not 1 <= source.max_articles_per_scan <= 100:
                raise ConfigurationError("Maximum articles per scan must be between 1 and 100")
            if not 1 <= source.max_listing_pages <= 25:
                raise ConfigurationError("Maximum listing pages must be between 1 and 25")
            try:
                re.compile(source.article_url_pattern)
            except re.error as error:
                raise ConfigurationError(f"Article URL pattern is invalid: {error}") from error
