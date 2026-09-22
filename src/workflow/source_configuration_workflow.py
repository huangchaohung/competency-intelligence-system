"""Officer-controlled source catalogue management."""
from src.models.domain import Source
from src.services.configuration_service import ConfigurationService
from src.services.source_service import SourceService


class SourceConfigurationWorkflow:
    """Keep YAML configuration and database source records in sync."""
    def __init__(self, configuration: ConfigurationService, sources: SourceService) -> None:
        self._configuration = configuration
        self._sources = sources

    def upsert(self, source: Source, previous_url: str | None = None, previous_id: int | None = None) -> Source:
        """Add a source or replace its selected catalogue entry, then persist it."""
        configured = self._configuration.load_sources()
        replacement = Source(previous_id, source.name.strip(), source.url.strip(), source.organisation.strip(), source.country.strip(), source.enabled, source.category.strip() or "Uncategorised", source.max_articles_per_scan, source.article_url_pattern.strip(), source.is_active, source.max_listing_pages, source.use_browser_rendering, source.evidence_label, source.source_type, source.source_role, source.llm_allowed, source.source_family)
        revised = [item for item in configured if item.url != (previous_url or replacement.url)]
        revised.append(replacement)
        self._configuration.save_sources(revised)
        return self._sources.persist(replacement)

    def remove(self, source_id: int, source_url: str | None = None) -> list[Source]:
        """Remove a source from the active catalogue without deleting evidence history."""
        configured = self._configuration.load_sources()
        remaining = [item for item in configured if item.id != source_id and item.url != source_url]
        self._configuration.save_sources(remaining)
        self._sources.persist_catalogue(remaining)
        return remaining

    def validate_catalogue(self, sources: list[Source]) -> None:
        """Validate a draft catalogue without changing configuration or database state."""
        self._configuration.validate_sources(sources)

    def replace_catalogue(self, sources: list[Source]) -> list[Source]:
        """Persist a validated catalogue to YAML and SQLite."""
        self._configuration.save_sources(sources)
        return self._sources.persist_catalogue(sources)

    def stage_test_set(self, identifiers: list[str]) -> list[Source]:
        """Enable only the explicitly named/URL-matched sources for a tuning scan.

        This is deliberately an explicit operation: the catalogue remains intact,
        but every other active source is disabled in both YAML and SQLite.  An
        identifier may be a source name, organisation, or exact URL (case-insensitive).
        Unknown identifiers fail fast so a mistyped test plan cannot silently scan
        the wrong sources.
        """
        configured = self._configuration.load_sources()
        wanted = {value.strip().casefold() for value in identifiers if value.strip()}
        if not wanted:
            raise ValueError("At least one source name, organisation, or URL is required")

        def matches(source: Source) -> bool:
            fields = (source.name.casefold(), source.organisation.casefold(), source.url.casefold())
            # Exact matches are preferred, but a distinctive partial name is
            # convenient for the command-line staging helper (e.g. "NASA
            # Systems Engineering" for the full Handbook title).
            return any(identifier == field or identifier in field for identifier in wanted for field in fields)

        matched = [source for source in configured if matches(source)]
        matched_text = {field for source in matched for field in (source.name.casefold(), source.organisation.casefold(), source.url.casefold())}
        missing = {identifier for identifier in wanted if not any(identifier == field or identifier in field for field in matched_text)}
        if missing:
            raise ValueError(f"Unknown source test identifier(s): {', '.join(sorted(missing))}")
        staged = [Source(source.id, source.name, source.url, source.organisation, source.country, matches(source), source.category, source.max_articles_per_scan, source.article_url_pattern, source.is_active, source.max_listing_pages, source.use_browser_rendering, source.evidence_label, source.source_type, source.source_role, source.llm_allowed, source.source_family) for source in configured]
        self._configuration.save_sources(staged)
        return self._sources.persist_catalogue(staged)

    def enable_all_active_sources(self) -> list[Source]:
        """Enable every active catalogue entry for a broad health baseline scan."""
        configured = self._configuration.load_sources()
        if not configured:
            raise ValueError("The source catalogue is empty")
        enabled = [Source(source.id, source.name, source.url, source.organisation, source.country, True, source.category, source.max_articles_per_scan, source.article_url_pattern, source.is_active, source.max_listing_pages, source.use_browser_rendering, source.evidence_label, source.source_type, source.source_role, source.llm_allowed, source.source_family) for source in configured]
        self._configuration.save_sources(enabled)
        return self._sources.persist_catalogue(enabled)
