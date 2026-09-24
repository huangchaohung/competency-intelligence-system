from src.models.domain import Source
from src.core.exceptions import ScanError
from src.scanner.article_discovery import ArticleDiscovery
from src.scanner.web_page_scanner import DownloadedPage


class FakeScanner:
    """In-memory scanner for article discovery tests."""
    def fetch_url(self, url: str, source_name: str) -> DownloadedPage:
        return DownloadedPage(url, '<a href="/articles/one">One</a><a href="/articles/two">Two</a><a href="https://other.example/articles/three">Outside</a><a href="/about">About</a><a href="/home/careers/">Careers</a><a href="/innovates/about-ntuie">About innovation</a><a href="/cdn-cgi/l/email-protection">Email</a><a href="/contact-us">Contact us</a><a href="/media/[resource:85:308023]">Placeholder</a><a href="/legal/privacy-statement">Privacy Statement</a><a href="/department-newsletter">Department Newsletter</a><a href="/st/ppid-info">Ad Privacy Options</a>')

    def is_allowed(self, url: str) -> bool:
        return not url.endswith("two")


def test_kaist_curriculum_navigation_is_bounded_and_permission_checked():
    from dataclasses import replace
    from src.models.domain import SourceType
    class Scanner:
        allowed = True
        def is_allowed(self, url):
            return self.allowed or url.endswith('sub030101')
        def fetch_url(self, url, name):
            return DownloadedPage(url, '<nav><a href="/english/sub030201">Table of Curriculum</a><a href="/english/sub030201#total">Total</a><a href="/english/people">People</a></nav><main><h1>Requirements</h1></main>')
    source = Source(1, 'KAIST', 'https://robots.kaist.ac.kr/english/sub030101', 'KAIST', source_type=SourceType.CATALOGUE)
    scanner = Scanner()
    discovery = ArticleDiscovery(scanner)
    assert discovery.discover_resources(source) == [source.url, 'https://robots.kaist.ac.kr/english/sub030201']
    assert discovery.discover_resources(replace(source, max_articles_per_scan=1)) == [source.url]
    scanner.allowed = False
    assert discovery.discover_resources(source) == [source.url]


class PaginationScanner:
    """Scanner fixture where pagination links should be followed but not stored."""

    def fetch_url(self, url: str, source_name: str) -> DownloadedPage:
        if "page=2" in url:
            return DownloadedPage(url, '<a href="/news/article-two">Article two</a>')
        return DownloadedPage(url, '<a href="/news?page=2">2</a><a href="/news/article-one">Article one</a>')

    def is_allowed(self, url: str) -> bool:
        return True


class PdfPatternScanner:
    """Scanner fixture with one matching article and one non-matching PDF."""

    def fetch_url(self, url: str, source_name: str) -> DownloadedPage:
        return DownloadedPage(url, '<a href="/media-article/good">Good article</a><a href="/assets/docs/noisy.pdf">PDF</a>')

    def is_allowed(self, url: str) -> bool:
        return True


class FailingListingScanner:
    """Scanner fixture where raw listing fetch fails after browser discovery."""

    def fetch_url(self, url: str, source_name: str) -> DownloadedPage:
        raise ScanError("Source response exceeds size limit")

    def is_allowed(self, url: str) -> bool:
        return True


class BrowserFallbackDiscovery(ArticleDiscovery):
    """Discovery fixture that simulates a successful browser-rendered pass."""

    def _discover_with_browser(self, source: Source) -> list[str]:
        return ["https://example.org/media-article/browser-good"]


class GovTechScanner:
    """Scanner fixture with GovTech article links mixed with product pages."""

    def fetch_url(self, url: str, source_name: str) -> DownloadedPage:
        return DownloadedPage(
            url,
            '<a href="/technews/ai-agents/">AI agents explained</a>'
            '<a href="/products-and-services/">Products and services</a>'
            '<a href="/media/official-announcement/">Announcement</a>',
        )

    def is_allowed(self, url: str) -> bool:
        return True


def test_discovery_limits_to_same_domain_pattern_and_cap() -> None:
    """Discovery never escapes a source domain or ignores robots decisions."""
    source = Source(None, "Test", "https://example.org/news", "Test", "Unknown", True, max_articles_per_scan=2, article_url_pattern=r"^/articles/")
    assert ArticleDiscovery(FakeScanner()).discover(source) == ["https://example.org/articles/one"]


def test_discovery_skips_utility_and_placeholder_links() -> None:
    """Discovery ignores utility URLs even when they are same-domain links."""
    source = Source(None, "Test", "https://example.org/news", "Test", "Unknown", True, max_articles_per_scan=10)
    assert ArticleDiscovery(FakeScanner()).discover(source) == ["https://example.org/articles/one"]


def test_discovery_uses_pagination_without_storing_listing_pages() -> None:
    """Pagination URLs are crawl navigation, not evidence records."""
    source = Source(None, "Test", "https://example.org/news", "Test", "Unknown", True, max_articles_per_scan=10)
    assert ArticleDiscovery(PaginationScanner()).discover(source) == [
        "https://example.org/news/article-one",
        "https://example.org/news/article-two",
    ]


def test_discovery_applies_article_pattern_before_accepting_pdfs() -> None:
    """Source URL patterns also constrain PDF candidates."""
    source = Source(None, "Test", "https://example.org/news", "Test", "Unknown", True, max_articles_per_scan=10, article_url_pattern=r"^/media-article/")
    assert ArticleDiscovery(PdfPatternScanner()).discover(source) == ["https://example.org/media-article/good"]


def test_discovery_keeps_browser_urls_when_raw_listing_fails() -> None:
    """A brittle raw listing page should not discard successful browser discovery."""
    source = Source(None, "Test", "https://example.org/news", "Test", "Unknown", True, max_articles_per_scan=10, article_url_pattern=r"^/media-article/", use_browser_rendering=True)
    assert BrowserFallbackDiscovery(FailingListingScanner()).discover(source) == ["https://example.org/media-article/browser-good"]


def test_discovery_applies_default_pattern_for_known_brittle_sources() -> None:
    """Known hubs remain scoped even when a stale database row has no configured pattern."""
    source = Source(None, "GovTech TechNews", "https://www.tech.gov.sg/technews/", "GovTech", "Singapore", True, max_articles_per_scan=10)
    assert ArticleDiscovery(GovTechScanner()).discover(source) == ["https://www.tech.gov.sg/technews/ai-agents/"]
