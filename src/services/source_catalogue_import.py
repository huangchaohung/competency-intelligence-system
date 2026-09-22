"""Helpers for safely staging a newly compiled source catalogue."""
from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit
import csv
from io import StringIO

from src.services.source_health_service import infer_source_type_from_url


def normalise_catalogue_url(value: str) -> str:
    """Normalize spreadsheet/TSV URL values without changing their destination."""
    url = str(value or "").strip().replace("\\:", ":")
    if not url:
        return ""
    parts = urlsplit(url)
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.casefold(), parts.netloc.casefold(), path, parts.query, ""))


def deduplicate_catalogue_rows(rows: list[dict]) -> list[dict]:
    """Keep the first row for each normalized URL, preserving distinct URLs."""
    seen: set[str] = set()
    result: list[dict] = []
    for row in rows:
        normalized = normalise_catalogue_url(row.get("Configured Discovery URL", row.get("url", "")))
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append({**row, "Configured Discovery URL": normalized})
    return result


def prepare_catalogue_rows(rows: list[dict]) -> list[dict]:
    """Prepare supplied rows for review without mutating the active catalogue."""
    staged = []
    for row in deduplicate_catalogue_rows(rows):
        url = row["Configured Discovery URL"]
        staged.append(
            {
                **row,
                "Configured Discovery URL": url,
                "Inferred Source Type": infer_source_type_from_url(url),
                "Import Status": "Staged for review",
            }
        )
    return staged


def catalogue_diff(active_rows: list[dict], staged_rows: list[dict]) -> dict[str, list[dict]]:
    """Compare staged rows to active rows by normalized configured URL."""
    def keyed(rows: list[dict]) -> dict[str, dict]:
        return {
            normalise_catalogue_url(row.get("Configured Discovery URL", row.get("url", ""))): row
            for row in rows
            if normalise_catalogue_url(row.get("Configured Discovery URL", row.get("url", "")))
        }
    active = keyed(active_rows)
    staged = keyed(staged_rows)
    return {
        "added": [staged[url] for url in sorted(set(staged) - set(active))],
        "removed": [active[url] for url in sorted(set(active) - set(staged))],
        "updated": [staged[url] for url in sorted(set(active) & set(staged)) if staged[url] != active[url]],
    }


def parse_catalogue_text(text: str) -> list[dict]:
    """Parse officer-provided CSV/TSV catalogue text into staging rows."""
    content = str(text or "").strip()
    if not content:
        return []
    dialect = csv.Sniffer().sniff(content[:4096], delimiters=",\t")
    return [dict(row) for row in csv.DictReader(StringIO(content), dialect=dialect)]
