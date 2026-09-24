"""Narrow browser retrieval for verified public NUS architecture curricula."""
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from src.core.exceptions import ScanError
from src.scanner.web_page_scanner import DownloadedPage, MAX_RESPONSE_BYTES
from src.scanner.browser_runtime import launch_chromium

PATHS = {
    '/arch/programmes/master-of-urban-planning/curriculum',
    '/arch/programmes/master-of-arts-in-urban-design/curriculum',
}


def matches(url):
    parsed = urlparse(url)
    return parsed.scheme == 'https' and parsed.netloc == 'cde.nus.edu.sg' and parsed.path.rstrip('/') in PATHS and not parsed.query


def fetch_curriculum(scanner, url):
    if not matches(url) or not scanner.is_allowed(url):
        raise ScanError('NUS curriculum browser retrieval is not permitted')
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as runtime:
            browser = launch_chromium(runtime)
            try:
                page = browser.new_page()
                response = page.goto(url, wait_until='domcontentloaded', timeout=20000)
                page.wait_for_timeout(1000)
                if response is not None and response.status >= 400:
                    raise ScanError(f'NUS curriculum returned HTTP {response.status}')
                if not matches(page.url) or not scanner.is_allowed(page.url):
                    raise ScanError('NUS curriculum redirected outside the permitted scope')
                html = page.content()
                if len(html.encode('utf-8')) > MAX_RESPONSE_BYTES:
                    raise ScanError('NUS curriculum rendered HTML exceeds size limit')
                visible = BeautifulSoup(html, 'lxml').get_text(' ', strip=True).lower()
                if 'incapsula incident id' in visible or not visible:
                    raise ScanError('NUS curriculum browser response is empty or access-blocked')
                return DownloadedPage(page.url, html)
            finally:
                browser.close()
    except ScanError:
        raise
    except Exception as error:
        raise ScanError(f'NUS curriculum browser retrieval failed: {type(error).__name__}') from error
