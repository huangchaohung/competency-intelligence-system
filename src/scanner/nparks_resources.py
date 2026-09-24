"""Scope NParks technical resources to their actual content, not site navigation."""
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from src.core.exceptions import ScanError

ROOTS = {
    '/services/research-programmes',
    '/who-we-are/city-in-nature-key-strategies',
    '/nature/enhancing-biodiversity-guidelines-resources',
}


def matches(url):
    parsed = urlparse(url)
    return parsed.hostname == 'www.nparks.gov.sg' and parsed.path.rstrip('/') in ROOTS


def discover(source, scanner):
    if not scanner.is_allowed(source.url):
        raise ScanError('NParks resource discovery is not permitted')
    page = scanner.fetch_url(source.url, source.name)
    if not matches(page.url):
        raise ScanError('NParks source redirected away from the configured resource')
    body = BeautifulSoup(page.html, 'lxml').select_one('.main-body')
    if body is None:
        raise ScanError('NParks resource content unavailable; refusing navigation-only discovery')
    root = urlparse(page.url)._replace(fragment='').geturl()
    urls = [root]
    path = urlparse(root).path.rstrip('/')
    # The strategy page is a standalone resource, not a general site index.
    if path == '/who-we-are/city-in-nature-key-strategies':
        return urls
    for link in body.select('a[href]'):
        parsed = urlparse(urljoin(root, link['href']))
        candidate = parsed._replace(fragment='').geturl()
        if len(urls) >= source.max_articles_per_scan:
            break
        if parsed.scheme != 'https' or parsed.netloc != 'www.nparks.gov.sg' or candidate in urls:
            continue
        permitted = (parsed.path.startswith(path + '/') or
                     (path.startswith('/nature/') and parsed.path.startswith('/docs/') and parsed.path.lower().endswith('.pdf')))
        if permitted and scanner.is_allowed(candidate):
            urls.append(candidate)
    return urls
