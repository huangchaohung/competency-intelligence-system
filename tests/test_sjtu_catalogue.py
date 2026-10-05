from unittest.mock import Mock
import pytest
from src.core.exceptions import ExtractionError, ScanError
from src.extractor.sjtu_catalogue import URL, catalogue_text
from src.scanner.web_page_scanner import DownloadedPage
from src.scanner.source_router import SourceRouter
from src.models.domain import Source
from src.extractor.article_extractor import ArticleExtractor
from src.workflow.scan_workflow import ScanWorkflow


def test_catalogue_extractor_preserves_provenance_without_admissions_page():
    source = Source(42, 'SJTU catalogue', URL, 'Shanghai Jiao Tong')
    text = '[PDF page 1] 2026 SJTU Undergraduate Program for International Students. Mechanical Engineering. '
    text += 'Programme information and study duration. ' * 25
    evidence = ArticleExtractor().extract(DownloadedPage(URL, '<article>'+text+'</article>', 'application/pdf'), source, 7)
    assert evidence.url == URL and evidence.source_id == 42 and evidence.scan_run_id == 7
    assert evidence.organisation == 'Shanghai Jiao Tong'
    assert 'mixed disciplines' in evidence.title
    assert 'non-STE' in evidence.article_text and '[PDF page 1]' in evidence.article_text
    assert not ScanWorkflow._is_utility_url(URL)
    admissions = 'https://global.sjtu.edu.cn/en/study-sjtu/prospective/degree-programs/387'
    assert ScanWorkflow._is_utility_url(admissions)
    assert ScanWorkflow._is_utility_url(admissions + '/')
    assert not ScanWorkflow._is_utility_url(admissions.replace('global.sjtu.edu.cn', 'other.example'))


def test_catalogue_extractor_rejects_redirect_or_empty_pdf():
    source = Source(42, 'SJTU catalogue', URL, 'Shanghai Jiao Tong')
    for page in (DownloadedPage('https://example.org/login', '<main>Login</main>'),
                 DownloadedPage(URL, '<article></article>', 'application/pdf')):
        with pytest.raises(ExtractionError):
            ArticleExtractor().extract(page, source, 7)


def test_catalogue_scope_and_page_markers_preserved():
    text = '[PDF page 1] 2026 SJTU Undergraduate Program for International Students. Mechanical Engineering. '
    text += 'Programme information and study duration. ' * 25
    result = catalogue_text(DownloadedPage(URL, '<article>'+text+'</article>', 'application/pdf'))
    assert '[PDF page 1]' in result and 'non-STE' in result
    assert 'not a full syllabus' in result
    for page in (DownloadedPage(URL, text), DownloadedPage('https://example.org/other.pdf', '<article>'+text+'</article>', 'application/pdf')):
        with pytest.raises(ExtractionError):
            catalogue_text(page)


def test_catalogue_discovery_checks_permission_without_html_discovery():
    scanner = Mock()
    scanner.is_allowed.return_value = True
    source = Source(1, 'SJTU catalogue', URL, 'SJTU')
    assert SourceRouter(scanner).discover(source) == [URL]
    scanner.fetch_url.assert_not_called()
    scanner.is_allowed.return_value = False
    with pytest.raises(ScanError):
        SourceRouter(scanner).discover(source)
