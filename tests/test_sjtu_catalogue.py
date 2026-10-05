from unittest.mock import Mock
import pytest
from src.core.exceptions import ExtractionError, ScanError
from src.extractor.sjtu_catalogue import URL, catalogue_text
from src.scanner.web_page_scanner import DownloadedPage
from src.scanner.source_router import SourceRouter
from src.models.domain import Source


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
