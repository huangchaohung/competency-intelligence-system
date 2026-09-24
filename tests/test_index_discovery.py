from src.models.domain import Source, SourceRole, SourceType
from src.scanner.article_discovery import ArticleDiscovery
from src.scanner.web_page_scanner import DownloadedPage


class FakeScanner:
    """In-memory scanner for index discovery tests."""
    def fetch_url(self, url: str, source_name: str) -> DownloadedPage:
        if url.endswith("/index"):
            return DownloadedPage(
                url,
                '<a href="/topic-a">Topic A</a><a href="/topic-b">Topic B</a><a href="https://other.example/topic-c">Outside</a>',
            )
        if url.endswith("/topic-a"):
            return DownloadedPage(url, '<a href="/topic-a-1">Child 1</a><a href="/topic-a-2">Child 2</a>')
        return DownloadedPage(url, "")

    def is_allowed(self, url: str) -> bool:
        return True


def test_index_discovery_is_same_domain_and_bounded() -> None:
    """Index traversal should stay same-domain and only traverse one level deep."""
    source = Source(
        None,
        "Index",
        "https://example.org/index",
        "Example Org",
        "Singapore",
        True,
        "Uncategorised",
        10,
        "",
        True,
        3,
        False,
        "news / commentary",
        SourceType.INDEX,
        SourceRole.PRIMARY_DISCOVERY,
        True,
    )

    urls = ArticleDiscovery(FakeScanner()).discover_index(source)

    assert "https://example.org/topic-a" in urls
    assert "https://example.org/topic-b" in urls
    assert "https://other.example/topic-c" not in urls
    assert "https://example.org/topic-a-1" in urls
    assert "https://example.org/topic-a-2" in urls
    assert len(urls) == 4
