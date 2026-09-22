"""SQLite persistence for sources."""
import sqlite3
from src.models.domain import Source, SourceFamily, SourceRole, SourceType


class SourceRepository:
    """Persist source records without applying business rules."""
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def upsert(self, source: Source) -> Source:
        """Insert or update a source by URL."""
        self._connection.execute("INSERT INTO sources(name,url,organisation,source_family,country,source_type,source_role,llm_allowed,enabled,category,evidence_label,max_articles_per_scan,article_url_pattern,is_active,max_listing_pages,use_browser_rendering) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(url) DO UPDATE SET name=excluded.name, organisation=excluded.organisation, source_family=excluded.source_family, country=excluded.country, source_type=excluded.source_type, source_role=excluded.source_role, llm_allowed=excluded.llm_allowed, enabled=excluded.enabled, category=excluded.category, evidence_label=excluded.evidence_label, max_articles_per_scan=excluded.max_articles_per_scan, article_url_pattern=excluded.article_url_pattern, is_active=excluded.is_active, max_listing_pages=excluded.max_listing_pages, use_browser_rendering=excluded.use_browser_rendering", (source.name, source.url, source.organisation, source.source_family.value, source.country, source.source_type.value, source.source_role.value, int(source.llm_allowed), source.enabled, source.category, source.evidence_label, source.max_articles_per_scan, source.article_url_pattern, source.is_active, source.max_listing_pages, source.use_browser_rendering))
        self._connection.commit()
        row = self._connection.execute("SELECT * FROM sources WHERE url=?", (source.url,)).fetchone()
        return self._to_source(row)

    def update(self, source: Source) -> Source:
        """Update an existing source by its immutable database identity."""
        if source.id is None:
            raise ValueError("A source ID is required for update")
        self._connection.execute("UPDATE sources SET name=?,url=?,organisation=?,source_family=?,country=?,source_type=?,source_role=?,llm_allowed=?,enabled=?,category=?,evidence_label=?,max_articles_per_scan=?,article_url_pattern=?,is_active=?,max_listing_pages=?,use_browser_rendering=? WHERE id=?", (source.name, source.url, source.organisation, source.source_family.value, source.country, source.source_type.value, source.source_role.value, int(source.llm_allowed), source.enabled, source.category, source.evidence_label, source.max_articles_per_scan, source.article_url_pattern, source.is_active, source.max_listing_pages, source.use_browser_rendering, source.id))
        self._connection.commit()
        row = self._connection.execute("SELECT * FROM sources WHERE id=?", (source.id,)).fetchone()
        if row is None:
            raise ValueError(f"Source does not exist: {source.id}")
        return self._to_source(row)

    def list_enabled(self) -> list[Source]:
        """Return enabled sources in stable name order."""
        rows = self._connection.execute("SELECT * FROM sources WHERE enabled=1 AND is_active=1 ORDER BY name").fetchall()
        return [self._to_source(row) for row in rows]

    def list_all(self) -> list[Source]:
        """Return all configured sources."""
        rows = self._connection.execute("SELECT * FROM sources WHERE is_active=1 ORDER BY name").fetchall()
        return [self._to_source(row) for row in rows]

    def retire_missing(self, active_urls: set[str]) -> None:
        """Soft-delete sources no longer present in the active catalogue."""
        placeholders = ",".join("?" for _ in active_urls) if active_urls else ""
        if active_urls:
            self._connection.execute(f"UPDATE sources SET is_active=0, enabled=0 WHERE url NOT IN ({placeholders})", tuple(active_urls))
        else:
            self._connection.execute("UPDATE sources SET is_active=0, enabled=0")
        self._connection.commit()

    @staticmethod
    def _to_source(row: sqlite3.Row) -> Source:
        return Source(
            row["id"],
            row["name"],
            row["url"],
            row["organisation"],
            row["country"] if "country" in row.keys() else "",
            bool(row["enabled"]),
            row["category"],
            row["max_articles_per_scan"],
            row["article_url_pattern"],
            bool(row["is_active"]) if "is_active" in row.keys() else True,
            row["max_listing_pages"] if "max_listing_pages" in row.keys() else 3,
            bool(row["use_browser_rendering"]) if "use_browser_rendering" in row.keys() else False,
            row["evidence_label"] if "evidence_label" in row.keys() else "news / commentary",
            SourceType(str(row["source_type"]) if "source_type" in row.keys() and row["source_type"] else SourceType.ARTICLE.value),
            SourceRole(str(row["source_role"]) if "source_role" in row.keys() and row["source_role"] else SourceRole.PRIMARY_DISCOVERY.value),
            bool(row["llm_allowed"]) if "llm_allowed" in row.keys() else True,
            SourceFamily(str(row["source_family"]) if "source_family" in row.keys() and row["source_family"] else SourceFamily.PROFESSIONAL_BODY.value),
        )
