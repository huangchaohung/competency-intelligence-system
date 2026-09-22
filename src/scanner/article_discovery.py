"""Controlled discovery of article links from approved source pages."""
import re
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup

from src.core.exceptions import ScanError
from src.models.domain import Source
from src.scanner.web_page_scanner import WebPageScanner
from src.scanner.browser_runtime import launch_chromium

try:
    from playwright.sync_api import sync_playwright
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
except ImportError:  # pragma: no cover - optional dependency
    sync_playwright = None
    PlaywrightTimeoutError = TimeoutError


class ArticleDiscovery:
    """Discover bounded, same-domain HTML article links for one source."""

    _BLOCKED_PREFIXES = (
        "/topic/", "/type/", "/tag/", "/author/", "/search", "/login", "/register", "/core/",
        "/media-library/", "/about", "/policy", "/advert", "/event", "/podcast", "/video",
        "/site/", "/rss", "/privacy", "/terms", "/magazine/", "/issue/", "/archive/", "/taxonomy/",
    )
    _BLOCKED_MARKERS = (
        "javascript:", "mailto:", "tel:", "[resource:", "/cdn-cgi/", "/email-protection",
        "facebook.com/", "twitter.com/", "x.com/", "linkedin.com/", "instagram.com/", "youtube.com/", "tiktok.com/",
    )
    _BLOCKED_PATH_PARTS = (
        "/contact", "/contact-us", "/careers", "/career", "/jobs", "/membership", "/login", "/register",
        "/privacy", "/terms", "/sitemap", "/newsletter", "/newsletters", "/subscribe", "/about-us",
        "/legal", "/form", "/facebook", "/twitter", "/linkedin", "/instagram", "/youtube", "/tiktok",
    )
    _BLOCKED_PATH_MARKERS = (
        "/about-us", "/legal/", "/privacy", "/contact", "newsletter", "/taxonomy/", "void(0)",
        "/st/ppid-info", "customised-programmess",
    )
    _ARTICLE_HINT_CLASSES = ("headline", "post-title", "custom-post-headline", "widget__headline-text", "story-title", "story_teaser")
    _RESOURCE_HINTS = (
        "competenc", "skill", "framework", "course", "programme", "program", "training", "certificate", "curriculum",
        "standard", "guidance", "resource", "research", "initiative", "hub", "library", "catalogue", "catalog",
    )
    _MONTH_NAMES = ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december")
    _BROWSER_SCROLL_STEPS = 10
    _BROWSER_SCROLL_PAUSE_MS = 800
    _TRUSTED_EXTERNAL_HOSTS = {"info.corenet.gov.sg", "www.ura.gov.sg", "ura.gov.sg"}

    def __init__(self, scanner: WebPageScanner) -> None:
        self._scanner = scanner

    def discover(self, source: Source) -> list[str]:
        """Return deduplicated candidate article URLs within the configured cap."""
        if not self._scanner.is_allowed(source.url):
            raise ScanError(f"robots.txt disallows discovery for {source.name}")

        browser_urls = self._discover_with_browser(source) if source.use_browser_rendering else []

        try:
            if self._is_raeng_news(source):
                urls = self._discover_raeng_news(source)
            elif self._is_govtech_listing(source):
                urls = self._discover_govtech_listing(source)
            elif self._is_engineers_australia_listing(source):
                urls = self._discover_paginated_listing(source, 1, 10)
            elif self._is_engc_listing(source):
                urls = self._discover_paginated_listing(source, 1, 10)
            elif self._is_nus_news_reports(source):
                urls = self._discover_nus_news_reports(source)
            elif self._is_resource_hub(source):
                urls = self._discover_resource_hub(source)
            elif self._is_ieee_spectrum(source):
                urls = self._discover_ieee(source)
            elif self._is_broad_news_source(source):
                urls = self._discover_broad_news(source)
            else:
                urls = self._discover_generic(source)
        except ScanError:
            if browser_urls:
                return browser_urls
            raise

        urls = self._merge_urls(browser_urls, urls)
        if not urls:
            raise ScanError(f"No permitted article links discovered for {source.name}; try a more specific discovery URL or article URL pattern")
        return urls

    def discover_index(self, source: Source) -> list[str]:
        """Discover same-domain child pages from an index hub with one bounded traversal step."""
        source_host = urlparse(source.url).hostname or ""
        urls: list[str] = []
        seen: set[str] = set()
        visited: set[str] = set()
        queue: list[tuple[str, int]] = [(source.url, 0)]
        while queue and len(urls) < source.max_articles_per_scan:
            listing_url, depth = queue.pop(0)
            if listing_url in visited:
                continue
            visited.add(listing_url)
            listing = self._scanner.fetch_url(listing_url, source.name)
            soup = BeautifulSoup(listing.html, "lxml")
            for link in soup.find_all("a", href=True):
                candidate = urldefrag(urljoin(listing.url, link.get("href") or ""))[0]
                if not self._accept_index_candidate(candidate, source, source_host, seen):
                    continue
                seen.add(candidate)
                urls.append(candidate)
                if len(urls) >= source.max_articles_per_scan:
                    break
                if depth == 0:
                    queue.append((candidate, depth + 1))
        return urls

    def discover_trend(self, source: Source) -> list[str]:
        """Discover trend/news hub articles with a slightly broader fallback strategy."""
        urls = self._discover_broad_news(source)
        if not urls:
            urls = self._discover_generic(source)
        if not urls and source.use_browser_rendering:
            urls = self._discover_with_browser(source)
        return urls

    def discover_resources(self, source: Source) -> list[str]:
        """Discover explicit competency/course/resource pages with resource-first filtering."""
        if not self._scanner.is_allowed(source.url):
            raise ScanError(f"robots.txt disallows discovery for {source.name}")
        source_host = urlparse(source.url).hostname or ""
        # The configured course/framework page can itself contain the evidence.
        # Extraction still applies its normal content and utility-page checks.
        urls: list[str] = [source.url]
        seen: set[str] = {source.url}
        listing_queue = [source.url]
        visited_listings: set[str] = set()

        while listing_queue and len(urls) < source.max_articles_per_scan and len(visited_listings) < source.max_listing_pages:
            listing_url = listing_queue.pop(0)
            if listing_url in visited_listings:
                continue
            visited_listings.add(listing_url)
            listing = self._scanner.fetch_url(listing_url, source.name)
            soup = BeautifulSoup(listing.html, "lxml")
            # KAIST places its companion curriculum in navigation, outside the
            # article body. Admit only the two reviewed curriculum destinations,
            # and only when an actual link is present on this configured source.
            kaist_curriculum = {
                'https://robots.kaist.ac.kr/english/sub030101',
                'https://robots.kaist.ac.kr/english/sub030201',
            }
            if source.url.rstrip('/') in kaist_curriculum:
                for link in soup.find_all('a', href=True):
                    candidate = urldefrag(urljoin(listing.url, link['href']))[0].rstrip('/')
                    if (candidate in kaist_curriculum and candidate not in seen
                            and len(urls) < source.max_articles_per_scan
                            and self._scanner.is_allowed(candidate)):
                        seen.add(candidate)
                        urls.append(candidate)
            for link in self._article_links(soup):
                candidate = urldefrag(urljoin(listing.url, link.get("href") or ""))[0]
                if self._accept_resource_candidate(candidate, link.get_text(" ", strip=True), link.get("href") or "", link.get("aria-label") or "", source, source_host, seen):
                    seen.add(candidate)
                    urls.append(candidate)
                    if len(urls) >= source.max_articles_per_scan:
                        break
            if len(urls) < source.max_articles_per_scan:
                for link in self._fallback_article_links(soup):
                    candidate = urldefrag(urljoin(listing.url, link.get("href") or ""))[0]
                    if self._accept_resource_candidate(candidate, link.get_text(" ", strip=True), link.get("href") or "", link.get("aria-label") or "", source, source_host, seen):
                        seen.add(candidate)
                        urls.append(candidate)
                        if len(urls) >= source.max_articles_per_scan:
                            break
            for next_link in self._pagination_links(soup, listing.url, source_host):
                if next_link not in visited_listings and next_link not in listing_queue:
                    listing_queue.append(next_link)
        if not urls:
            return self._discover_generic(source)
        return urls

    def _discover_generic(self, source: Source) -> list[str]:
        source_host = urlparse(source.url).hostname or ""
        pattern = self._effective_article_pattern(source)
        urls: list[str] = []
        seen: set[str] = set()
        listing_queue = [source.url]
        visited_listings: set[str] = set()

        while listing_queue and len(urls) < source.max_articles_per_scan:
            listing_url = listing_queue.pop(0)
            if listing_url in visited_listings:
                continue
            visited_listings.add(listing_url)
            listing = self._scanner.fetch_url(listing_url, source.name)
            soup = BeautifulSoup(listing.html, "lxml")
            for link in self._article_links(soup):
                candidate = urldefrag(urljoin(listing.url, link.get("href") or ""))[0]
                if self._accept_candidate(candidate, link.get_text(" ", strip=True), link.get("href") or "", link.get("aria-label") or "", source, source_host, seen, pattern):
                    seen.add(candidate)
                    urls.append(candidate)
                    if len(urls) >= source.max_articles_per_scan:
                        break
            if len(urls) < source.max_articles_per_scan:
                for link in self._fallback_article_links(soup):
                    candidate = urldefrag(urljoin(listing.url, link.get("href") or ""))[0]
                    if self._accept_candidate(candidate, link.get_text(" ", strip=True), link.get("href") or "", link.get("aria-label") or "", source, source_host, seen, pattern):
                        seen.add(candidate)
                        urls.append(candidate)
                        if len(urls) >= source.max_articles_per_scan:
                            break
            for next_link in self._pagination_links(soup, listing.url, source_host):
                if next_link not in visited_listings and next_link not in listing_queue:
                    listing_queue.append(next_link)
        return urls

    def _discover_raeng_news(self, source: Source) -> list[str]:
        """Discover Royal Academy news cards from pages 1-5 using page buttons."""
        source_host = urlparse(source.url).hostname or ""
        urls: list[str] = []
        seen: set[str] = set()

        def collect_from_html(html: str, base_url: str) -> None:
            nonlocal urls
            soup = BeautifulSoup(html, "lxml")
            selectors = "#news-search-results .card h3.card-title a[href], #news-search-results a.card-title[href], .card h3 a[href]"
            for card in soup.select(selectors):
                candidate = urldefrag(urljoin(base_url, card.get("href") or ""))[0]
                if self._accept_candidate(candidate, card.get_text(" ", strip=True), card.get("href") or "", card.get("aria-label") or "", source, source_host, seen, None):
                    seen.add(candidate)
                    urls.append(candidate)
                    if len(urls) >= source.max_articles_per_scan:
                        return

        if source.use_browser_rendering and sync_playwright is not None:
            with sync_playwright() as playwright:
                browser = launch_chromium(playwright)
                page = browser.new_page(viewport={"width": 1440, "height": 2200}, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
                try:
                    page.goto(source.url, wait_until="domcontentloaded", timeout=30_000)
                except PlaywrightTimeoutError:
                    page.goto(source.url, wait_until="commit", timeout=10_000)
                self._dismiss_cookie_banner(page)
                collect_from_html(page.content(), source.url)
                for page_number in range(2, 6):
                    if len(urls) >= source.max_articles_per_scan:
                        break
                    button = page.locator(f"input.js-page-number-trigger[data-target-page='{page_number}']")
                    if button.count() == 0:
                        continue
                    button.first.click(timeout=10_000)
                    page.wait_for_load_state("domcontentloaded", timeout=30_000)
                    self._dismiss_cookie_banner(page)
                    collect_from_html(page.content(), source.url)
                browser.close()

        if len(urls) < source.max_articles_per_scan:
            listing = self._scanner.fetch_url(source.url, source.name)
            collect_from_html(listing.html, listing.url)

        return urls

    def _discover_govtech_listing(self, source: Source) -> list[str]:
        """Discover GovTech media/technews cards across pages 1-10."""
        return self._discover_paginated_listing(source, 1, 10)

    def _discover_paginated_listing(self, source: Source, start_page: int, end_page: int) -> list[str]:
        """Discover article links from numbered listing pages."""
        source_host = urlparse(source.url).hostname or ""
        pattern = self._effective_article_pattern(source)
        urls: list[str] = []
        seen: set[str] = set()
        base = source.url.split("?")[0].rstrip("/") + "/"
        for page_number in range(start_page, end_page + 1):
            if len(urls) >= source.max_articles_per_scan:
                break
            listing_url = f"{base}?page={page_number}"
            try:
                listing = self._scanner.fetch_url(listing_url, source.name)
            except ScanError:
                continue
            soup = BeautifulSoup(listing.html, "lxml")
            for link in soup.find_all("a", href=True):
                candidate = urldefrag(urljoin(listing.url, link.get("href") or ""))[0]
                if self._accept_candidate(candidate, link.get_text(" ", strip=True), link.get("href") or "", link.get("aria-label") or "", source, source_host, seen, pattern):
                    seen.add(candidate)
                    urls.append(candidate)
                    if len(urls) >= source.max_articles_per_scan:
                        break
        return urls

    def _discover_ieee(self, source: Source) -> list[str]:
        """Discover IEEE Spectrum article cards from topic/listing pages."""
        source_host = urlparse(source.url).hostname or ""
        pattern = self._effective_article_pattern(source)
        urls: list[str] = []
        seen: set[str] = set()
        queue = [source.url]
        visited: set[str] = set()
        while queue and len(urls) < source.max_articles_per_scan:
            listing_url = queue.pop(0)
            if listing_url in visited:
                continue
            visited.add(listing_url)
            listing = self._scanner.fetch_url(listing_url, source.name)
            soup = BeautifulSoup(listing.html, "lxml")
            for link in self._ieee_article_links(soup):
                candidate = urldefrag(urljoin(listing.url, link.get("href") or ""))[0]
                if self._accept_candidate(candidate, link.get_text(" ", strip=True), link.get("href") or "", link.get("aria-label") or "", source, source_host, seen, pattern):
                    seen.add(candidate)
                    urls.append(candidate)
                    if len(urls) >= source.max_articles_per_scan:
                        break
            for next_link in self._pagination_links(soup, listing.url, source_host):
                if next_link not in visited and next_link not in queue:
                    queue.append(next_link)
        if not urls:
            return self._discover_generic(source)
        return urls

    def _discover_broad_news(self, source: Source) -> list[str]:
        """Aggressively discover links from pages that expose article cards imperfectly."""
        source_host = urlparse(source.url).hostname or ""
        pattern = self._effective_article_pattern(source)
        urls: list[str] = []
        seen: set[str] = set()
        queue = [source.url]
        visited: set[str] = set()
        while queue and len(urls) < source.max_articles_per_scan:
            listing_url = queue.pop(0)
            if listing_url in visited:
                continue
            visited.add(listing_url)
            listing = self._scanner.fetch_url(listing_url, source.name)
            soup = BeautifulSoup(listing.html, "lxml")
            for link in soup.find_all("a", href=True):
                candidate = urldefrag(urljoin(listing.url, link.get("href") or ""))[0]
                if self._accept_candidate(candidate, link.get_text(" ", strip=True), link.get("href") or "", link.get("aria-label") or "", source, source_host, seen, pattern):
                    seen.add(candidate)
                    urls.append(candidate)
                    if len(urls) >= source.max_articles_per_scan:
                        break
            for next_link in self._pagination_links(soup, listing.url, source_host):
                if next_link not in visited and next_link not in queue:
                    queue.append(next_link)
        if not urls:
            return self._discover_generic(source)
        return urls

    def _discover_with_browser(self, source: Source) -> list[str]:
        """Render a listing page in a browser and collect links after scrolling."""
        if not source.use_browser_rendering:
            return []
        if sync_playwright is None:
            raise ScanError("Browser rendering requires Playwright; install it to enable scrolling sources")
        source_host = urlparse(source.url).hostname or ""
        pattern = self._effective_article_pattern(source)
        urls: list[str] = []
        seen: set[str] = set()
        with sync_playwright() as playwright:
            browser = launch_chromium(playwright)
            page = browser.new_page(viewport={"width": 1440, "height": 2200}, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
            try:
                page.goto(source.url, wait_until="domcontentloaded", timeout=20_000)
            except PlaywrightTimeoutError:
                try:
                    page.goto(source.url, wait_until="commit", timeout=10_000)
                except PlaywrightTimeoutError:
                    browser.close()
                    return []
            self._dismiss_cookie_banner(page)
            previous_height = 0
            for _ in range(self._BROWSER_SCROLL_STEPS):
                page.mouse.wheel(0, 4000)
                page.wait_for_timeout(self._BROWSER_SCROLL_PAUSE_MS)
                try:
                    for button_text in ("Load more", "Show more", "More", "Next"):
                        locator = page.get_by_role("button", name=re.compile(button_text, re.I))
                        if locator.count() > 0:
                            locator.first.click(timeout=2_000)
                            page.wait_for_timeout(self._BROWSER_SCROLL_PAUSE_MS)
                            break
                except Exception:
                    pass
                try:
                    current_height = int(page.evaluate("document.body.scrollHeight"))
                    if current_height == previous_height:
                        break
                    previous_height = current_height
                except Exception:
                    break
            html = page.content()
            browser.close()
        soup = BeautifulSoup(html, "lxml")
        for link in self._article_links(soup):
            candidate = urldefrag(urljoin(source.url, link.get("href") or ""))[0]
            if self._accept_candidate(candidate, link.get_text(" ", strip=True), link.get("href") or "", link.get("aria-label") or "", source, source_host, seen, pattern):
                seen.add(candidate)
                urls.append(candidate)
                if len(urls) >= source.max_articles_per_scan:
                    break
        return urls

    def _discover_nus_news_reports(self, source: Source) -> list[str]:
        """Discover NUS news reports with cookie dismissal and scrolling."""
        source_host = urlparse(source.url).hostname or ""
        pattern = self._effective_article_pattern(source)
        if sync_playwright is None:
            return self._discover_generic(source)
        urls: list[str] = []
        seen: set[str] = set()
        with sync_playwright() as playwright:
            browser = launch_chromium(playwright)
            page = browser.new_page(viewport={"width": 1440, "height": 2200}, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
            try:
                page.goto(source.url, wait_until="domcontentloaded", timeout=20_000)
            except PlaywrightTimeoutError:
                page.goto(source.url, wait_until="commit", timeout=10_000)
            self._dismiss_cookie_banner(page)
            for _ in range(6):
                page.mouse.wheel(0, 4000)
                page.wait_for_timeout(1000)
            soup = BeautifulSoup(page.content(), "lxml")
            browser.close()
        for link in self._article_links(soup):
            candidate = urldefrag(urljoin(source.url, link.get("href") or ""))[0]
            if self._accept_candidate(candidate, link.get_text(" ", strip=True), link.get("href") or "", link.get("aria-label") or "", source, source_host, seen, pattern):
                seen.add(candidate)
                urls.append(candidate)
                if len(urls) >= source.max_articles_per_scan:
                    break
        return urls

    def _discover_resource_hub(self, source: Source) -> list[str]:
        """Discover document and article links from resource-hub style pages."""
        source_host = urlparse(source.url).hostname or ""
        pattern = self._effective_article_pattern(source)
        urls: list[str] = []
        seen: set[str] = set()
        queue = [source.url]
        visited: set[str] = set()
        while queue and len(urls) < source.max_articles_per_scan:
            listing_url = queue.pop(0)
            if listing_url in visited:
                continue
            visited.add(listing_url)
            listing = self._scanner.fetch_url(listing_url, source.name)
            soup = BeautifulSoup(listing.html, "lxml")
            for link in soup.find_all("a", href=True):
                candidate = urldefrag(urljoin(listing.url, link.get("href") or ""))[0]
                if self._accept_candidate(candidate, link.get_text(" ", strip=True), link.get("href") or "", link.get("aria-label") or "", source, source_host, seen, pattern):
                    seen.add(candidate)
                    urls.append(candidate)
                    if len(urls) >= source.max_articles_per_scan:
                        break
            for next_link in self._pagination_links(soup, listing.url, source_host):
                if next_link not in visited and next_link not in queue:
                    queue.append(next_link)
        return urls

    @staticmethod
    def _dismiss_cookie_banner(page) -> None:
        for text in ("accept all cookies", "accept cookies", "accept", "agree", "i understand", "i agree"):
            try:
                button = page.get_by_role("button", name=re.compile(text, re.I))
                if button.count() > 0:
                    button.first.click(timeout=2_000)
                    page.wait_for_timeout(1000)
                    return
            except Exception:
                continue

    def _accept_candidate(self, candidate: str, text: str, href: str, aria: str, source: Source, source_host: str, seen: set[str], pattern: re.Pattern[str] | None) -> bool:
        parsed = urlparse(candidate)
        candidate_host = parsed.hostname or ""
        if parsed.scheme != "https":
            return False
        if self._is_blocked_url(candidate, parsed.path):
            return False
        if not self._is_same_domain(candidate_host, source_host) and not self._is_trusted_external_candidate(source, candidate_host):
            return False
        if candidate == source.url or candidate in seen:
            return False
        if parsed.path in ("", "/"):
            return False
        if self._is_blocked_url(candidate, parsed.path):
            return False
        if parsed.path.startswith(self._BLOCKED_PREFIXES):
            return False
        if self._looks_like_issue_archive(parsed.path, text, aria):
            return False
        if pattern and not pattern.search(parsed.path):
            return False
        if parsed.path.lower().endswith(".pdf") or href.lower().endswith(".pdf"):
            return self._scanner.is_allowed(candidate)
        if not self._looks_like_article(text, href, parsed.path):
            return False
        if not self._scanner.is_allowed(candidate):
            return False
        return True

    @staticmethod
    def _effective_article_pattern(source: Source) -> re.Pattern[str] | None:
        """Return configured or source-specific URL constraints for brittle hubs."""
        if source.article_url_pattern:
            return re.compile(source.article_url_pattern)
        url = source.url.lower()
        if "tech.gov.sg/media" in url:
            return re.compile(r"^/media/.+")
        if "tech.gov.sg/technews" in url:
            return re.compile(r"^/technews/.+")
        if "theiet.org/impact-society/policy-and-public-affairs/education-and-skills-policy/reports-and-papers/uk-skills-surveys" in url:
            return re.compile(r"^/impact-society/policy-and-public-affairs/education-and-skills-policy/reports-and-papers/uk-skills-surveys(?:/.*)?$")
        if "asme.org/codes-standards" in url:
            return re.compile(r"^/codes-standards(?:/.*)?$")
        return None

    def _accept_resource_candidate(self, candidate: str, text: str, href: str, aria: str, source: Source, source_host: str, seen: set[str]) -> bool:
        parsed = urlparse(candidate)
        if parsed.scheme != "https":
            return False
        if self._is_blocked_url(candidate, parsed.path):
            return False
        if candidate == source.url or candidate in seen:
            return False
        if not self._is_same_domain(parsed.hostname or "", source_host) and not self._is_trusted_external_candidate(source, parsed.hostname or ""):
            return False
        if parsed.path in ("", "/"):
            return False
        if self._is_blocked_url(candidate, parsed.path):
            return False
        if parsed.path.startswith(self._BLOCKED_PREFIXES):
            return False
        tokens = f"{text} {href} {aria} {parsed.path}".lower()
        if not any(hint in tokens for hint in self._RESOURCE_HINTS):
            return False
        if parsed.path.lower().endswith(".pdf") or href.lower().endswith(".pdf"):
            return self._scanner.is_allowed(candidate)
        if not self._scanner.is_allowed(candidate):
            return False
        return True

    def _accept_index_candidate(self, candidate: str, source: Source, source_host: str, seen: set[str]) -> bool:
        parsed = urlparse(candidate)
        if parsed.scheme != "https":
            return False
        if self._is_blocked_url(candidate, parsed.path):
            return False
        if candidate == source.url or candidate in seen:
            return False
        if not self._is_same_domain(parsed.hostname or "", source_host):
            return False
        if parsed.path in ("", "/"):
            return False
        if self._is_blocked_url(candidate, parsed.path):
            return False
        if parsed.path.startswith(self._BLOCKED_PREFIXES):
            return False
        if not self._scanner.is_allowed(candidate):
            return False
        return True

    @staticmethod
    def _is_trusted_external_candidate(source: Source, candidate_host: str) -> bool:
        return "institution of engineers singapore" in source.organisation.lower() and candidate_host in ArticleDiscovery._TRUSTED_EXTERNAL_HOSTS

    @staticmethod
    def _merge_urls(primary: list[str], secondary: list[str]) -> list[str]:
        merged: list[str] = []
        seen: set[str] = set()
        for url in primary + secondary:
            if url not in seen:
                seen.add(url)
                merged.append(url)
        return merged

    @staticmethod
    def _is_same_domain(candidate_host: str, source_host: str) -> bool:
        return candidate_host == source_host or candidate_host.endswith(f".{source_host}")

    @staticmethod
    def _is_blocked_url(candidate: str, path: str) -> bool:
        value = candidate.lower()
        path_value = path.lower().rstrip("/")
        if any(marker in value for marker in ArticleDiscovery._BLOCKED_MARKERS):
            return True
        if any(part == path_value or path_value.startswith(f"{part}/") for part in ArticleDiscovery._BLOCKED_PATH_PARTS):
            return True
        if any(marker in path_value for marker in ArticleDiscovery._BLOCKED_PATH_MARKERS):
            return True
        blocked_segments = {
            "about", "about-us", "careers", "contact", "contact-us", "jobs", "legal",
            "login", "membership", "privacy", "register", "sitemap", "subscribe", "terms",
        }
        if any(segment == blocked or segment.startswith(f"{blocked}-") for segment in path_value.split("/") if segment for blocked in blocked_segments):
            return True
        parsed = urlparse(candidate)
        if parsed.query:
            query = parsed.query.lower()
            if (
                query.startswith("page=")
                or "&page=" in query
                or query.startswith("f%5b")
                or "&f%5b" in query
                or query.startswith("year=")
                or "&year=" in query
                or query.startswith("category=")
                or "&category=" in query
                or query.startswith("ucam-ref=")
                or "&ucam-ref=" in query
            ):
                return True
        return False

    @staticmethod
    def _looks_like_article(text: str, href: str, path: str) -> bool:
        tokens = (text + " " + href + " " + path).lower()
        return (
            any(marker in tokens for marker in ("article", "news", "blog", "press", "speech", "insight", "research", "publication", "post", "story", "release"))
            or any(marker in href.lower() for marker in ("/2025/", "/2026/", "/news/", "/blog/", "/posts/", "/press-releases/", "/articles/"))
            or len(text.split()) >= 3
            or len(path.strip("/").split("/")) <= 2 and bool(path.strip("/"))
        )

    @staticmethod
    def _looks_like_issue_archive(path: str, text: str, aria: str) -> bool:
        tokens = f"{path} {text} {aria}".lower()
        if any(month in tokens for month in ArticleDiscovery._MONTH_NAMES) and re.search(r"\b20\d{2}\b", tokens):
            return True
        return "issue" in tokens or "archive" in tokens or "magazine" in tokens or "issue-" in tokens

    @staticmethod
    def _article_links(soup: BeautifulSoup):
        # Site menus can consume the entire article budget before content links.
        for menu in soup.select("nav, header, footer, [role='navigation']"):
            menu.decompose()
        links = []
        for article in soup.find_all("article"):
            links.extend(article.find_all("a", href=True))
        if not links:
            links = soup.find_all("a", href=True)
        return links

    @staticmethod
    def _fallback_article_links(soup: BeautifulSoup):
        links = []
        for link in soup.find_all("a", href=True):
            classes = " ".join(link.get("class", [])).lower()
            aria = (link.get("aria-label") or "").strip()
            title = (link.get("title") or "").strip()
            if any(hint in classes for hint in ArticleDiscovery._ARTICLE_HINT_CLASSES) or aria or title:
                links.append(link)
        return links

    @staticmethod
    def _ieee_article_links(soup: BeautifulSoup):
        links = []
        selectors = [
            "article h2 a[href]",
            "article h3 a[href]",
            "a.widget__headline-text[href]",
            "a[aria-label][href]",
            "article a[href]",
        ]
        for selector in selectors:
            links.extend(soup.select(selector))
        filtered = []
        seen: set[str] = set()
        for link in links:
            href = link.get("href") or ""
            classes = " ".join(link.get("class", [])).lower()
            label = (link.get("aria-label") or link.get_text(" ", strip=True)).lower()
            if "story_teaser" in classes or "widget__headline" in classes or "headline" in classes or label or href:
                if href not in seen:
                    seen.add(href)
                    filtered.append(link)
        return filtered

    @staticmethod
    def _is_ieee_spectrum(source: Source) -> bool:
        url = source.url.lower()
        return "spectrum.ieee.org/" in url and ("/topic/" in url or url.rstrip("/").endswith("spectrum.ieee.org"))

    @staticmethod
    def _is_raeng_news(source: Source) -> bool:
        url = source.url.lower().rstrip("/")
        return "raeng.org.uk/news" in url and "/news" in url

    @staticmethod
    def _is_govtech_listing(source: Source) -> bool:
        url = source.url.lower()
        return "tech.gov.sg/media" in url or "tech.gov.sg/technews" in url

    @staticmethod
    def _is_engineers_australia_listing(source: Source) -> bool:
        return "engineersaustralia.org.au/news-and-media" in source.url.lower()

    @staticmethod
    def _is_engc_listing(source: Source) -> bool:
        return "engc.org.uk/news-and-insights" in source.url.lower()

    @staticmethod
    def _is_nus_news_reports(source: Source) -> bool:
        return "news.nus.edu.sg/news-reports" in source.url.lower()

    @staticmethod
    def _is_broad_news_source(source: Source) -> bool:
        url = source.url.lower()
        return any(domain in url for domain in ("engx.theiet.org/b/", "wsg.gov.sg/home/media-room/media-releases-speeches"))

    @staticmethod
    def _is_resource_hub(source: Source) -> bool:
        url = source.url.lower()
        return any(domain in url for domain in (
            "raeng.org.uk/education-and-skills/schools/stem-resources",
            "engineerscanada.ca/guidelines-and-papers/public-guideline-on-admission-to-the-practice-of-engineering-in-canada",
            "www.asme.org/codes-standards",
            "www.asce.org/publications-and-news/codes-and-standards/",
            "www.nspe.org/resources/professional-development/events",
        ))

    @staticmethod
    def _pagination_links(soup: BeautifulSoup, base_url: str, source_host: str) -> list[str]:
        links: list[str] = []
        for link in soup.find_all("a", href=True):
            text = link.get_text(" ", strip=True).lower()
            href = link["href"].lower()
            rel = " ".join(link.get("rel", [])).lower()
            aria = (link.get("aria-label") or "").lower()
            numbered_page = re.search(r"[?&]page=\d+(?:[&#]|$)", href) or re.search(r"/page/\d+(?:[/?#]|$)", href)
            if text.strip() not in {"next", "next page", "next ›", "next »"} and "next" not in rel.split() and aria.strip() != "next page" and not numbered_page:
                continue
            candidate = urldefrag(urljoin(base_url, link["href"]))[0]
            parsed = urlparse(candidate)
            if any(part in parsed.path.lower().split("/") for part in ("form", "forms", "page-feedback", "login", "contact")):
                continue
            if parsed.scheme == "https" and ArticleDiscovery._is_same_domain(parsed.hostname or "", source_host):
                links.append(candidate)
        return links
