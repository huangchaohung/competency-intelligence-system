"""Bounded subject-first discovery for the broad Harvard PLL catalogue."""
from collections import deque
from itertools import zip_longest
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from src.core.exceptions import ScanError

ROOT = 'https://pll.harvard.edu/catalog'
SUBJECTS = ('computer-science', 'data-science', 'mathematics', 'programming', 'science')
LOGGER = logging.getLogger(__name__)


def discover(source, scanner):
    queue = deque('https://pll.harvard.edu/subject/' + name for name in SUBJECTS)
    groups = []
    visited = set()
    errors = []
    for _ in range(source.max_listing_pages):
        if not queue:
            break
        url = queue.popleft()
        visited.add(url)
        try:
            if not scanner.is_allowed(url):
                raise ScanError('Harvard subject discovery not permitted')
            page = scanner.fetch_url(url, source.name)
            if page.url != url:
                raise ScanError('Harvard subject listing redirected')
            soup = BeautifulSoup(page.html, 'lxml')
            listing = soup.select_one('.views-id-catalog')
            if listing is None:
                raise ScanError('Harvard subject listing unavailable')
            urls = []
            for link in listing.select('h3 a[href]'):
                candidate = urlparse(urljoin(url, link['href']))._replace(fragment='').geturl()
                parsed = urlparse(candidate)
                if (parsed.scheme == 'https' and parsed.netloc == 'pll.harvard.edu'
                        and parsed.path.startswith('/course/') and not parsed.query
                        and candidate not in urls and scanner.is_allowed(candidate)):
                    urls.append(candidate)
            groups.append(urls)
            for link in soup.select('.pager a[href]'):
                candidate = urlparse(urljoin(url, link['href']))._replace(fragment='').geturl()
                parsed = urlparse(candidate)
                # Drupal's page=0 is the unparameterised first page, not a
                # new listing. Do not spend the request budget on it twice.
                if parsed.query == 'page=0':
                    candidate = parsed._replace(query='').geturl()
                    parsed = urlparse(candidate)
                if (parsed.scheme == 'https' and parsed.netloc == 'pll.harvard.edu'
                        and parsed.path == urlparse(url).path and parsed.query.startswith('page=')
                        and parsed.query[5:].isdigit() and candidate not in visited and candidate not in queue):
                    queue.append(candidate)
        except ScanError as error:
            errors.append(str(error))
            LOGGER.warning('Harvard subject listing skipped: %s (%s)', url, error)
    result = []
    for row in zip_longest(*groups):
        for url in row:
            if url and url not in result:
                result.append(url)
                if len(result) >= source.max_articles_per_scan:
                    return result
    if not result and errors:
        raise ScanError('; '.join(dict.fromkeys(errors)))
    return result
