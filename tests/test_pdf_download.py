from types import SimpleNamespace
import pytest
from src.core.exceptions import ScanError
from src.scanner.web_page_scanner import WebPageScanner


def response(chunks):
    return SimpleNamespace(iter_content=lambda size: iter(chunks), close=lambda: None,
                           url='https://example.org/report.pdf')


def test_pdf_rejects_html_challenge():
    with pytest.raises(ScanError, match='non-PDF'):
        WebPageScanner()._download_pdf(response([b'<html>Request unsuccessful</html>']), 'Test')


def test_pdf_parser_failure_is_scan_error():
    with pytest.raises(ScanError, match='Unable to extract PDF'):
        WebPageScanner()._download_pdf(response([b'%PDF-1.7 corrupt']), 'Test')


def test_pdf_limit_stops_stream_and_closes(monkeypatch):
    monkeypatch.setattr('src.scanner.web_page_scanner.MAX_RESPONSE_BYTES', 5)
    closed = []
    def chunks(size):
        yield b'%PDF-1.7'
        pytest.fail('Must not consume rest of oversized download')
    item = SimpleNamespace(iter_content=chunks, close=lambda: closed.append(True))
    with pytest.raises(ScanError, match='size limit'):
        WebPageScanner()._download_pdf(item, 'Test')
    assert closed == [True]
