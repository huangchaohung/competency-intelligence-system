"""Bounded browser retrieval of the reviewed public ICT framework overview."""
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from src.core.exceptions import ScanError
from src.scanner.web_page_scanner import DownloadedPage, MAX_RESPONSE_BYTES
from src.scanner.browser_runtime import launch_chromium

URL = 'https://www.imda.gov.sg/how-we-can-help/techskills-accelerator-tesa/skills-framework-for-infocomm-technology-sfw-for-ict'
SELECTOR = 'main article.detail-content'
GENAI_PDF_URL = 'https://www.imda.gov.sg/assets/f9e0ac04-898f-4de7-bc89-e6b34aa2e7d8.pdf'


def matches(url):
    p = urlparse(url)
    return p.scheme == 'https' and p.netloc == 'www.imda.gov.sg' and p.path.rstrip('/') == urlparse(URL).path and not p.query


def overview_text(html):
    if len(html.encode('utf-8')) > MAX_RESPONSE_BYTES:
        raise ScanError('IMDA rendered HTML exceeds size limit')
    soup = BeautifulSoup(html, 'lxml')
    body = soup.select_one(SELECTOR)
    if body is None:
        raise ScanError('IMDA content block unavailable')
    for node in body.select('script, style, nav, form, #Contact'):
        node.decompose()
    text = body.get_text('\n', strip=True)
    lowered = text.casefold()
    if any(x in lowered for x in ('you do not have access', 'access denied', 'incapsula incident id')):
        raise ScanError('IMDA overview access-blocked')
    if len(text.split()) < 100 or 'skills framework' not in lowered or 'ict' not in lowered:
        raise ScanError('Insufficient IMDA framework overview text')
    # Preserve auditable document references without claiming PDF retrieval.
    # Only the two reviewed link labels inside the main overview are admitted.
    references = []
    seen = set()
    for link in body.select('a[href]'):
        label = link.get_text(' ', strip=True)
        target = urljoin(URL, link['href'])
        parsed = urlparse(target)
        if (label in {'Navigate SFw for ICT', 'New skills in GenAI'}
                and parsed.scheme == 'https' and parsed.netloc == 'www.imda.gov.sg'
                and parsed.path.startswith('/assets/') and parsed.path.lower().endswith('.pdf')
                and not parsed.query and not parsed.fragment and target not in seen):
            seen.add(target)
            references.append(f'{label}: {target}')
    if references:
        text += '\n\nLinked documents (not retrieved or analysed):\n' + '\n'.join(references)
    return text


def fetch_overview(scanner, url):
    if not matches(url) or not scanner.is_allowed(url):
        raise ScanError('IMDA overview retrieval is not permitted')
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as runtime:
            browser = launch_chromium(runtime)
            try:
                page = browser.new_page()
                response = page.goto(url, wait_until='domcontentloaded', timeout=20000)
                if response is not None and response.status >= 400:
                    raise ScanError(f'IMDA overview returned HTTP {response.status}')
                if not matches(page.url) or not scanner.is_allowed(page.url):
                    raise ScanError('IMDA overview redirected away from permitted scope')
                page.wait_for_selector(SELECTOR, timeout=10000)
                # The container mounts before its client-loaded text arrives.
                # Wait for content, not network-idle (analytics may never idle).
                page.wait_for_function("""selector => {
                    const text = document.querySelector(selector)?.innerText || '';
                    return text.trim().split(/\\s+/).length >= 100;
                }""", arg=SELECTOR, timeout=10000)
                html = page.content()
                overview_text(html)
                return DownloadedPage(page.url, html)
            finally:
                browser.close()
    except ScanError:
        raise
    except Exception as error:
        raise ScanError(f'IMDA browser retrieval failed: {type(error).__name__}') from error
