"""Stage the next scan from a source-health CSV without deleting catalogue rows.

Healthy and low-output sources remain enabled. Error/no-evidence sources are
disabled for tuning and remain available for URL replacement or later removal.
"""
from pathlib import Path
import csv
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.database import connect, initialise
from src.models.domain import Source
from src.repositories.source_repository import SourceRepository
from src.services.configuration_service import ConfigurationService
from src.services.source_service import SourceService
from src.services.source_catalogue_import import normalise_catalogue_url


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/apply_source_health_stage.py <source_health.csv>")
        return 2
    health_path = Path(sys.argv[1])
    health = {}
    with health_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            url = normalise_catalogue_url(row.get("Source URL", ""))
            if url:
                health[url] = str(row.get("Status", "")).strip().casefold()
    configuration = ConfigurationService(ROOT / "config" / "sources.yaml")
    connection = connect(ROOT / "data" / "competency_intelligence.db")
    initialise(connection)
    service = SourceService(SourceRepository(connection))
    configured = configuration.load_sources()
    staged = []
    changed = {"disabled": 0, "kept": 0, "unmatched": 0}
    for source in configured:
        status = health.get(normalise_catalogue_url(source.url))
        enabled = status in {"healthy", "low evidence"} if status else source.enabled
        if status is None:
            changed["unmatched"] += 1
        elif enabled:
            changed["kept"] += 1
        else:
            changed["disabled"] += 1
        staged.append(Source(source.id, source.name, source.url, source.organisation, source.country, enabled, source.category, source.max_articles_per_scan, source.article_url_pattern, source.is_active, source.max_listing_pages, source.use_browser_rendering, source.evidence_label, source.source_type, source.source_role, source.llm_allowed, source.source_family))
    configuration.save_sources(staged)
    service.persist_catalogue(staged)
    print(f"Kept enabled (healthy/low evidence): {changed['kept']}")
    print(f"Disabled (error/no evidence): {changed['disabled']}")
    print(f"Unmatched catalogue rows left unchanged: {changed['unmatched']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
