"""Engineering course links from Ngee Ann's reviewed full-time listing."""
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from src.core.exceptions import ScanError

ROOT = 'https://www.np.edu.sg/schools-courses/academic-schools/school-of-engineering'


def matches(url):
    return url.rstrip('/') == ROOT


def is_course(url):
    parsed = urlparse(url)
    root = urlparse(ROOT)
    tail = parsed.path.removeprefix(root.path + '/').strip('/')
    return (parsed.scheme == 'https' and parsed.netloc == root.netloc
            and parsed.path.startswith(root.path + '/') and '/' not in tail
            and (tail.startswith('diploma-in-') or tail == 'common-engineering-programme'))


def discover(source, scanner):
    if not scanner.is_allowed(source.url):
        raise ScanError('NP engineering discovery is not permitted')
    page = scanner.fetch_url(source.url, source.name)
    if not matches(page.url):
        raise ScanError('NP engineering redirected away from the listing')
    listing = BeautifulSoup(page.html, 'lxml').select_one('main #full-time-courses')
    if listing is None:
        raise ScanError('NP engineering course listing unavailable')
    urls = []
    for link in listing.select('a[href]'):
        parsed = urlparse(urljoin(page.url, link['href']))
        url = parsed._replace(fragment='').geturl()
        if is_course(url) and not parsed.query and url not in urls and scanner.is_allowed(url):
            urls.append(url)
        if len(urls) >= source.max_articles_per_scan:
            break
    return urls
