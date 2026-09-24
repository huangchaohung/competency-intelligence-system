"""Bounded HTTP retrieval for configured public pages."""
from dataclasses import dataclass
import logging
from io import BytesIO
from html import escape
import requests
from bs4 import BeautifulSoup, UnicodeDammit
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from src.core.exceptions import ScanError
from src.models.domain import Source

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - optional dependency
    PdfReader = None

LOGGER = logging.getLogger(__name__)
MAX_RESPONSE_BYTES = 2_000_000
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass(frozen=True)
class DownloadedPage:
    """A downloaded HTML response kept only in memory."""
    url: str
    html: str
    content_type: str = "text/html"


class WebPageScanner:
    """Download configured public HTML with conservative safety limits."""
    def __init__(self) -> None:
        self._robots_cache: dict[str, RobotFileParser | None] = {}

    def fetch(self, source: Source) -> DownloadedPage:
        """Fetch one HTML source or raise ScanError."""
        return self.fetch_url(source.url, source.name)

    def fetch_url(self, url: str, source_name: str) -> DownloadedPage:
        """Fetch one approved HTTPS URL or raise ScanError."""
        try:
            response = requests.get(url, timeout=(5, 20), headers=DEFAULT_HEADERS, stream=True)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
                return self._download_pdf(response, source_name)
            if "html" not in content_type.lower():
                raise ScanError(f"Source did not return HTML: {source_name}")
            chunks: list[bytes] = []
            total_bytes = 0
            for chunk in response.iter_content(8192):
                total_bytes += len(chunk)
                if total_bytes > MAX_RESPONSE_BYTES:
                    raise ScanError(f"Source response exceeds size limit: {source_name}")
                chunks.append(chunk)
            content = b"".join(chunks)
            LOGGER.info("Downloaded source '%s'", source_name)
            # Requests assumes Latin-1 for text/html without an HTTP charset,
            # even when the document declares UTF-8 in a meta tag.
            declared = [response.encoding] if 'charset=' in content_type.lower().replace(' ', '') and response.encoding else []
            html = UnicodeDammit(content, known_definite_encodings=declared, is_html=True).unicode_markup
            visible = BeautifulSoup(html or '', 'lxml').get_text(' ', strip=True).casefold()
            # Some access gateways return HTTP 200, not an HTTP error. Do not
            # mistake their short incident notice for an empty course catalogue.
            if (len(visible.split()) < 100 and 'request unsuccessful' in visible
                    and 'incapsula incident id' in visible):
                raise ScanError(f'Access blocked by Incapsula; no source content retrieved: {source_name}')
            readable = BeautifulSoup(html or '', 'lxml')
            for element in readable.select('script, style, head, template'):
                element.decompose()
            if not readable.get_text(' ', strip=True):
                raise ScanError(
                    f'No readable HTML content retrieved: {source_name}. '
                    'The response may require browser rendering or be access-restricted; '
                    'this does not establish that the source has no information.')
            return DownloadedPage(response.url, html or '', content_type="text/html")
        except requests.RequestException as error:
            raise ScanError(f"Unable to download {source_name}: {error}") from error

    def _download_pdf(self, response: requests.Response, source_name: str) -> DownloadedPage:
        """Download a PDF and expose its extracted text as article-like HTML."""
        if PdfReader is None:
            raise ScanError(f"PDF extraction requires pypdf for {source_name}")
        chunks = []
        total = 0
        try:
            for chunk in response.iter_content(8192):
                total += len(chunk)
                if total > MAX_RESPONSE_BYTES:
                    raise ScanError(f"Source response exceeds size limit: {source_name}")
                chunks.append(chunk)
        finally:
            response.close()
        content = b''.join(chunks)
        if b'%PDF-' not in content[:1024]:
            raise ScanError(f"Expected PDF but received non-PDF content: {source_name}")
        try:
            reader = PdfReader(BytesIO(content))
            pages_text: list[str] = []
            for page in reader.pages:
                text = (page.extract_text() or "").strip()
                if text:
                    pages_text.append(text)
        except Exception as error:
            raise ScanError(f"Unable to extract PDF text: {source_name} ({type(error).__name__})") from error
        if not pages_text:
            raise ScanError(f"No extractable text found in PDF for {source_name}")
        text = "\n\n".join(pages_text)
        paragraphs = ''.join(f'<p>{escape(part)}</p>' for part in pages_text)
        html = f"<html><head><title>{escape(source_name)}</title></head><body><article>{paragraphs}</article></body></html>"
        LOGGER.info("Downloaded PDF source '%s'", source_name)
        return DownloadedPage(response.url, html, content_type="application/pdf")

    def is_allowed(self, url: str) -> bool:
        """Check a URL against its public robots.txt rules for this user agent."""
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        parser = self._robots_cache.get(robots_url)
        if parser is None and robots_url in self._robots_cache:
            return False
        if parser is None:
            try:
                response = requests.get(robots_url, timeout=(5, 10), headers=DEFAULT_HEADERS)
                if response.status_code == 404:
                    parser = RobotFileParser()
                    parser.parse(["User-agent: *", "Allow: /"])
                else:
                    response.raise_for_status()
                    parser = RobotFileParser()
                    parser.parse(response.text.splitlines())
                self._robots_cache[robots_url] = parser
            except requests.RequestException as error:
                LOGGER.warning("Unable to read robots.txt for '%s': %s", parsed.netloc, error)
                self._robots_cache[robots_url] = None
                return False
        return parser.can_fetch(DEFAULT_HEADERS["User-Agent"], url)
