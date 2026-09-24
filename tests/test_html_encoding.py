from types import SimpleNamespace
from src.scanner.web_page_scanner import WebPageScanner


def test_html_meta_charset_overrides_requests_default(monkeypatch):
    html = '<meta charset="utf-8"><p>Engineering—design and robots</p>'
    response = SimpleNamespace(headers={'Content-Type': 'text/html'}, encoding='ISO-8859-1',
        url='https://example.org', raise_for_status=lambda: None,
        iter_content=lambda size: [html.encode('utf-8')])
    monkeypatch.setattr('src.scanner.web_page_scanner.requests.get', lambda *a, **kw: response)
    assert WebPageScanner().fetch_url(response.url, 'Test').html == html


def test_explicit_non_utf8_charset_is_preserved(monkeypatch):
    html = '<p>Énergie et ingénierie</p>'
    response = SimpleNamespace(headers={'Content-Type': 'text/html; charset=windows-1252'}, encoding='windows-1252',
        url='https://example.org', raise_for_status=lambda: None,
        iter_content=lambda size: [html.encode('windows-1252')])
    monkeypatch.setattr('src.scanner.web_page_scanner.requests.get', lambda *a, **kw: response)
    assert WebPageScanner().fetch_url(response.url, 'Test').html == html
