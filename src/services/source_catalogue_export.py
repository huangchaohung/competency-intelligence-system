"""Export source catalogue records for officer review and IT backup."""
from __future__ import annotations

import csv
import io
from typing import Iterable

import yaml

from src.models.domain import Source


OFFICER_COLUMNS = [
    "Name",
    "Organisation",
    "Source family",
    "Source type",
    "Source role",
    "Discovery URL",
    "Max articles",
    "Listing pages",
    "Browser rendering",
    "LLM fallback allowed",
]


IT_COLUMNS = [
    *OFFICER_COLUMNS,
    "Enabled",
    "Active",
    "Article URL pattern",
]


def source_rows(sources: Iterable[Source], include_backend_fields: bool = False) -> list[dict[str, object]]:
    """Return source rows suitable for CSV export."""
    rows: list[dict[str, object]] = []
    for source in sources:
        row: dict[str, object] = {
            "Name": source.name,
            "Organisation": source.organisation,
            "Source family": source.source_family.value,
            "Source type": source.source_type.value,
            "Source role": source.source_role.value,
            "Discovery URL": source.url,
            "Max articles": source.max_articles_per_scan,
            "Listing pages": source.max_listing_pages,
            "Browser rendering": "Yes" if source.use_browser_rendering else "No",
            "LLM fallback allowed": "Yes" if source.llm_allowed else "No",
        }
        if include_backend_fields:
            row.update(
                {
                    "Enabled": "Yes" if source.enabled else "No",
                    "Active": "Yes" if source.is_active else "No",
                    "Article URL pattern": source.article_url_pattern,
                }
            )
        rows.append(row)
    return rows


def sources_csv(sources: Iterable[Source], include_backend_fields: bool = False) -> str:
    """Return source catalogue rows as CSV text."""
    columns = IT_COLUMNS if include_backend_fields else OFFICER_COLUMNS
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(source_rows(sources, include_backend_fields=include_backend_fields))
    return buffer.getvalue()


def sources_yaml_backup(sources: Iterable[Source]) -> str:
    """Return a YAML backup matching the app's source configuration format."""
    document = {
        "sources": [
            {
                "name": source.name,
                "url": source.url,
                "organisation": source.organisation,
                "source_family": source.source_family.value,
                "source_type": source.source_type.value,
                "source_role": source.source_role.value,
                "llm_allowed": source.llm_allowed,
                "max_articles_per_scan": source.max_articles_per_scan,
                "article_url_pattern": source.article_url_pattern,
                "enabled": source.enabled,
                "max_listing_pages": source.max_listing_pages,
                "use_browser_rendering": source.use_browser_rendering,
            }
            for source in sources
            if source.is_active
        ]
    }
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True)
