from types import SimpleNamespace
import pytest
from src.scanner import web_page_scanner as module
from src.core.exceptions import ScanError


def response(html):
    return SimpleNamespace(headers={'Content-Type': 'text/html'}, encoding=None,
        url='https://example.org/course', raise_for_status=lambda: None,
        iter_content=lambda size: [html.encode()])


def test_empty_incapsula_shell_is_access_error_without_leaking_query(monkeypatch):
    monkeypatch.setattr(module.requests, 'get', lambda *a, **kw: response(
        '<html><script src="/_Incapsula_Resource?secret=PRIVATE"></script></html>'))
    with pytest.raises(ScanError, match='Access blocked by Incapsula security shell') as caught:
        module.WebPageScanner().fetch_url('https://example.org/course', 'Course')
    assert 'PRIVATE' not in str(caught.value)


def test_substantive_content_with_security_script_is_not_rejected(monkeypatch):
    html = '<main>' + 'Engineering competencies and course descriptions. ' * 30 + '</main>'
    html += '<script src="/_Incapsula_Resource?x=1"></script>'
    monkeypatch.setattr(module.requests, 'get', lambda *a, **kw: response(html))
    assert module.WebPageScanner().fetch_url('https://example.org/course', 'Course').html == html
