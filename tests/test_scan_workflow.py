from src.models.domain import Source, SourceFamily, SourceRole, SourceType
from src.workflow.scan_workflow import ScanWorkflow
from unittest.mock import Mock
from types import SimpleNamespace
from datetime import datetime
from src.models.domain import ScanStatus


def test_redirect_duplicates_are_stored_once_per_run_but_allowed_next_run():
    source = Source(1, 'Research', 'https://example.org/research', 'Org')
    sources = Mock()
    sources.list_enabled.return_value = [source]
    scans = Mock()
    scans.create_run.return_value = SimpleNamespace(id=1)
    scans.complete_run.return_value = SimpleNamespace(id=1, status=ScanStatus.COMPLETED,
        started_at=datetime.now(), completed_at=datetime.now(), error_summary=None)
    scans.prune_evidence_to_recent_runs.return_value = 0
    scanner = Mock()
    scanner.fetch_url.return_value = SimpleNamespace(url='https://example.org/research/paper')
    extractor = Mock()
    extractor.extract.return_value = SimpleNamespace(url='https://example.org/research/paper')
    workflow = ScanWorkflow(sources, scans, scanner, extractor)
    workflow._router = Mock()
    workflow._router.discover.return_value = ['https://example.org/old-paper', 'https://example.org/new-paper']
    workflow.run()
    assert scans.add_evidence.call_count == 1
    assert extractor.extract.call_count == 1
    workflow.run()
    assert scans.add_evidence.call_count == 2


def test_scan_workflow_identifies_utility_urls() -> None:
    """Workflow has a final guard against storing navigation and utility pages."""
    assert ScanWorkflow._is_utility_url("https://example.org/news?page=2")
    assert ScanWorkflow._is_utility_url("https://example.org/legal/privacy-statement")
    assert ScanWorkflow._is_utility_url("https://example.org/department-newsletter")
    assert ScanWorkflow._is_utility_url("https://example.org/home/careers/")
    assert ScanWorkflow._is_utility_url("https://example.org/innovates/about-ntuie")
    assert not ScanWorkflow._is_utility_url("https://example.org/career-growth/ethics/nspe-code-ethics-engineers")
    assert ScanWorkflow._is_utility_url("https://example.org/whats-on/spotlight?year=2026")
    assert ScanWorkflow._is_utility_url("https://example.org/what-we-do?category=e")
    assert ScanWorkflow._is_utility_url("https://example.org/news?ucam-ref=home-menu")
    assert ScanWorkflow._is_utility_url("https://spectrum.ieee.org/st/ppid-info")
    assert not ScanWorkflow._is_utility_url("https://example.org/news/good-engineering-article")
    assert not ScanWorkflow._is_utility_url('https://www.istructe.org/about-us/what-we-do/events-and-training/')
    assert ScanWorkflow._is_utility_url('https://www.istructe.org/about-us/')
    assert ScanWorkflow._is_utility_url('https://example.org/about-us/what-we-do/events-and-training/')


def test_scan_workflow_applies_default_source_scope_for_brittle_hubs() -> None:
    """Known listing hubs are constrained even when old DB rows have blank patterns."""
    assert ScanWorkflow._matches_source_scope(
        "https://www.tech.gov.sg/technews/ai-agents/",
        "https://www.tech.gov.sg/technews/",
        "",
    )
    assert not ScanWorkflow._matches_source_scope(
        "https://www.tech.gov.sg/products-and-services/",
        "https://www.tech.gov.sg/technews/",
        "",
    )
    assert ScanWorkflow._matches_source_scope(
        "https://www.asme.org/codes-standards/find-codes-standards",
        "https://www.asme.org/codes-standards",
        "",
    )
    assert not ScanWorkflow._matches_source_scope(
        "https://www.asme.org/topics-resources",
        "https://www.asme.org/codes-standards",
        "",
    )


def test_scan_workflow_source_snapshot_keeps_health_and_fallback_metadata() -> None:
    """Batch source snapshots keep the metadata needed for History health checks."""
    source = Source(
        42,
        "GovTech TechNews",
        "https://www.tech.gov.sg/technews/",
        "GovTech",
        "Singapore",
        source_type=SourceType.TREND,
        source_role=SourceRole.TREND_VALIDATION,
        llm_allowed=False,
        source_family=SourceFamily.GOVERNMENT_AGENCY,
    )

    snapshot = ScanWorkflow._source_snapshot(source)

    assert snapshot["id"] == 42
    assert snapshot["llm_allowed"] is False
    assert snapshot["source_family"] == "GOVERNMENT_AGENCY"
    assert snapshot["source_type"] == "TREND"
    assert snapshot["source_role"] == "TREND_VALIDATION"
