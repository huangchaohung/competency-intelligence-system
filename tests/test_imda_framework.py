from types import SimpleNamespace
import pytest
from src.scanner.imda_framework import URL, matches, overview_text, fetch_overview
from src.scanner.source_router import SourceRouter
from src.scanner.web_page_scanner import DownloadedPage
from src.extractor.article_extractor import ArticleExtractor
from src.models.domain import Source
from src.core.exceptions import ScanError, ExtractionError


def test_genai_pdf_is_direct_and_requires_real_pdf_content():
    from src.scanner.imda_framework import GENAI_PDF_URL
    source = Source(1, 'IMDA GenAI', GENAI_PDF_URL, 'IMDA')
    assert SourceRouter(SimpleNamespace(is_allowed=lambda u: True)).discover(source) == [GENAI_PDF_URL]
    text = 'Generative AI skill description knowledge abilities. ' * 25
    html = '<article>'+text+'</article>'
    result = ArticleExtractor().extract(DownloadedPage(GENAI_PDF_URL, html, 'application/pdf'), source, 1)
    assert result.explicit_or_inferred == 'EXPLICIT'
    assert 'multi-column reading order' in result.article_text
    with pytest.raises(ExtractionError):
        ArticleExtractor().extract(DownloadedPage(GENAI_PDF_URL, html), source, 1)
    with pytest.raises(ExtractionError):
        ArticleExtractor().extract(DownloadedPage(GENAI_PDF_URL, '<article>empty</article>', 'application/pdf'), source, 1)
    with pytest.raises(ScanError):
        SourceRouter(SimpleNamespace(is_allowed=lambda u: False)).discover(source)


def test_imda_scope_and_overview_provenance():
    source = Source(1, 'IMDA ICT', URL, 'IMDA')
    text = 'Skills Framework ICT technical skills and career pathways. ' * 15
    html = '<main><nav>NOISE</nav><article class="detail-content">'+text+'<section id="Contact">CONTACT</section></article></main>'
    scanner = SimpleNamespace(is_allowed=lambda url: True)
    assert SourceRouter(scanner).discover(source) == [URL]
    result = ArticleExtractor().extract(DownloadedPage(URL, html), source, 1)
    assert 'linked framework documents were not retrieved' in result.article_text
    assert 'NOISE' not in result.article_text and 'CONTACT' not in result.article_text
    assert not matches(URL+'?other=1')
    with pytest.raises(ExtractionError):
        ArticleExtractor().extract(DownloadedPage('https://www.imda.gov.sg/', html), source, 1)
    with pytest.raises(ScanError, match='not permitted'):
        fetch_overview(SimpleNamespace(is_allowed=lambda url: False), URL)


@pytest.mark.parametrize('html', ['<main>Loading...</main>',
    '<main><article class="detail-content">Loading...</article></main>',
    '<main><article class="detail-content">You do not have access</article></main>'])
def test_imda_rejects_empty_loading_and_denied_responses(html):
    with pytest.raises(ScanError):
        overview_text(html)


def test_document_references_are_scoped_and_not_claimed_as_retrieved():
    text = 'Skills Framework ICT technical skills and career pathways. ' * 15
    links = ('<a href="/assets/framework.pdf">Navigate SFw for ICT</a>' * 2
             + '<a href="/assets/genai.pdf">New skills in GenAI</a>'
             + '<a href="https://other.example/foreign.pdf">New skills in GenAI</a>'
             + '<a href="/assets/tracking.pdf?secret=1">New skills in GenAI</a>')
    result = overview_text('<main><article class="detail-content">'+text+links+'</article></main>')
    assert 'Linked documents (not retrieved or analysed)' in result
    assert result.count('https://www.imda.gov.sg/assets/framework.pdf') == 1
    assert 'https://www.imda.gov.sg/assets/genai.pdf' in result
    assert 'other.example' not in result and 'secret=1' not in result


def test_browser_waits_for_content_and_closes_on_failure(monkeypatch):
    from unittest.mock import MagicMock
    import playwright.sync_api
    from src.scanner import imda_framework
    runtime = MagicMock()
    monkeypatch.setattr(playwright.sync_api, 'sync_playwright', lambda: runtime)
    browser = MagicMock()
    monkeypatch.setattr(imda_framework, 'launch_chromium', lambda p: browser)
    page = browser.new_page.return_value
    page.goto.return_value.status = 200
    page.url = URL
    page.content.return_value = '<main>Loading...</main>'
    with pytest.raises(ScanError):
        fetch_overview(SimpleNamespace(is_allowed=lambda u: True), URL)
    page.wait_for_function.assert_called_once()
    assert page.wait_for_function.call_args.kwargs['timeout'] == 10000
    browser.close.assert_called_once()
