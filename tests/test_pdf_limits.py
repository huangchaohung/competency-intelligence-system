from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from src.scanner import web_page_scanner as module
from src.core.exceptions import ScanError


def test_larger_limit_only_for_exact_reviewed_final_url(monkeypatch):
    scanner = module.WebPageScanner()
    scanner.is_allowed = lambda url: True
    scanner._download_pdf = Mock(return_value='parsed')
    url = next(iter(module.REVIEWED_LARGE_PDFS))
    response = SimpleNamespace(url=url, headers={'Content-Type': 'application/pdf'}, raise_for_status=lambda: None)
    monkeypatch.setattr(module.requests, 'get', lambda *a, **kw: response)
    scanner.fetch_url(url, 'Framework')
    assert scanner._download_pdf.call_args.kwargs['max_bytes'] == 8_000_000
    response.url = 'https://other.example/file.pdf'
    scanner.fetch_url(url, 'Framework')
    assert scanner._download_pdf.call_args.kwargs['max_bytes'] == 2_000_000
    scanner.fetch_url('https://example.org/file.pdf', 'Other')
    assert scanner._download_pdf.call_args.kwargs['max_bytes'] == 2_000_000


@pytest.mark.parametrize('kind', ['bytes', 'pages', 'text'])
def test_pdf_resource_limits_reject_without_partial_evidence(monkeypatch, kind):
    response = Mock()
    response.iter_content.return_value = [b'%PDF-1.7 test']
    response.url = 'https://example.org/file.pdf'
    pages = [SimpleNamespace(extract_text=lambda: 'abcd')]
    monkeypatch.setattr(module, 'PdfReader', lambda stream: SimpleNamespace(pages=pages))
    if kind == 'pages':
        monkeypatch.setattr(module, 'MAX_PDF_PAGES', 0)
    if kind == 'text':
        monkeypatch.setattr(module, 'MAX_PDF_TEXT_CHARS', 2)
    with pytest.raises(ScanError, match='limit'):
        module.WebPageScanner()._download_pdf(response, 'Test', max_bytes=2 if kind == 'bytes' else 100)
    response.close.assert_called_once()
