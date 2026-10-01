import pytest
from dataclasses import replace
from src.extractor.ict_sections import extract_sections
from src.scanner.web_page_scanner import DownloadedPage, ICT_FRAMEWORK_URL
from src.models.domain import Source
from src.core.exceptions import ExtractionError


def test_sections_preserve_pages_and_never_silently_truncate():
    text = 'Skills Framework ICT competencies technical knowledge. ' * 25
    html = '<article>'+''.join(f'<p>[PDF page {n}]\n{text}</p>' for n in [1, 50, 51, 561])+'</article>'
    page = DownloadedPage(ICT_FRAMEWORK_URL, html, 'application/pdf')
    source = Source(1, 'ICT', ICT_FRAMEWORK_URL, 'IMDA', max_articles_per_scan=25)
    records = extract_sections(page, source, 3)
    assert len(records) == 3
    assert [r.url.rsplit('=', 1)[1] for r in records] == ['1', '51', '561']
    assert '[PDF page 50]' in records[0].article_text
    assert all(r.scan_run_id == 3 for r in records)
    source = replace(source, max_articles_per_scan=1)
    with pytest.raises(ExtractionError, match='no partial'):
        extract_sections(page, source, 3)


@pytest.mark.parametrize('html', ['<article><p>Missing marker</p></article>',
    '<article><p>[PDF page 601] bad</p></article>', '<article></article>'])
def test_sections_reject_bad_page_coverage(html):
    with pytest.raises(ExtractionError):
        extract_sections(DownloadedPage(ICT_FRAMEWORK_URL, html, 'application/pdf'),
                         Source(1, 'ICT', ICT_FRAMEWORK_URL, 'IMDA'), 1)


def test_workflow_downloads_once_and_stores_distinct_sections():
    from unittest.mock import Mock
    from types import SimpleNamespace
    from datetime import datetime
    from src.workflow.scan_workflow import ScanWorkflow
    from src.models.domain import ScanStatus
    source = Source(1, 'ICT', ICT_FRAMEWORK_URL, 'IMDA', max_articles_per_scan=25)
    sources, scans, scanner, extractor = Mock(), Mock(), Mock(), Mock()
    sources.list_enabled.return_value = [source]
    scans.create_run.return_value = SimpleNamespace(id=1)
    scans.complete_run.return_value = SimpleNamespace(id=1, status=ScanStatus.COMPLETED,
        started_at=datetime.now(), completed_at=datetime.now(), error_summary=None)
    scans.prune_evidence_to_recent_runs.return_value = 0
    text = 'Skills Framework ICT competencies technical knowledge. ' * 25
    scanner.fetch_url.return_value = DownloadedPage(ICT_FRAMEWORK_URL,
        '<article>'+''.join(f'<p>[PDF page {n}] {text}</p>' for n in [1, 51])+'</article>', 'application/pdf')
    workflow = ScanWorkflow(sources, scans, scanner, extractor)
    workflow._router = SimpleNamespace(discover=lambda s: [ICT_FRAMEWORK_URL])
    workflow.run()
    scanner.fetch_url.assert_called_once()
    assert scans.add_evidence.call_count == 2
    assert [c.args[0].url for c in scans.add_evidence.call_args_list] == [ICT_FRAMEWORK_URL+'#page=1', ICT_FRAMEWORK_URL+'#page=51']
    extractor.extract.assert_not_called()
