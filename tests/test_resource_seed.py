from types import SimpleNamespace
import pytest
from src.scanner.article_discovery import ArticleDiscovery
from src.models.domain import Source
from src.core.exceptions import ScanError


class Scanner:
    def is_allowed(self, url):
        return True

    def fetch_url(self, url, name):
        return SimpleNamespace(url=url, html="<main><h1>Course curriculum</h1><p>Engineering course details.</p></main>")


def test_standalone_resource_is_included_without_child_links():
    source = Source(None, "Course", "https://example.org/course", "University")
    assert ArticleDiscovery(Scanner()).discover_resources(source) == [source.url]


def test_blocked_resource_is_not_submitted_for_extraction():
    scanner = Scanner()
    scanner.is_allowed = lambda url: False
    with pytest.raises(ScanError, match="robots.txt"):
        ArticleDiscovery(scanner).discover_resources(Source(None, "Course", "https://example.org/course", "University"))
