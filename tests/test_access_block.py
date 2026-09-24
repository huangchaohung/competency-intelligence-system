from types import SimpleNamespace

import pytest

from src.core.exceptions import ScanError
from src.scanner.web_page_scanner import WebPageScanner


def install_response(monkeypatch, html):
    response = SimpleNamespace(
        headers={'Content-Type': 'text/html; charset=utf-8'}, encoding='utf-8',
        url='https://example.org/course', raise_for_status=lambda: None,
        iter_content=lambda size: iter([html.encode('utf-8')]),
    )
    monkeypatch.setattr('src.scanner.web_page_scanner.requests.get', lambda *a, **k: response)


def test_http_success_with_incapsula_notice_is_access_error(monkeypatch):
    install_response(monkeypatch, '<html><body>Request unsuccessful. Incapsula incident ID: 123</body></html>')
    with pytest.raises(ScanError, match='Access blocked by Incapsula'):
        WebPageScanner().fetch_url('https://example.org/course', 'Course')


def test_article_discussing_access_blocks_is_not_rejected(monkeypatch):
    html = '<article>Request unsuccessful. Incapsula incident ID: example. ' + 'security training content ' * 50 + '</article>'
    install_response(monkeypatch, html)
    assert WebPageScanner().fetch_url('https://example.org/course', 'Course').html == html


@pytest.mark.parametrize('html', ['', '<html><head><title>Course</title></head><body><script>load()</script></body></html>'])
def test_empty_or_script_only_response_is_not_evidence(monkeypatch, html):
    install_response(monkeypatch, html)
    with pytest.raises(ScanError, match='No readable HTML content retrieved'):
        WebPageScanner().fetch_url('https://example.org/course', 'Course')


def test_short_real_content_with_security_script_is_not_blocked(monkeypatch):
    html = '<p>Power engineering course</p><script src="/_Incapsula_Resource"></script>'
    install_response(monkeypatch, html)
    assert WebPageScanner().fetch_url('https://example.org/course', 'Course').html == html
