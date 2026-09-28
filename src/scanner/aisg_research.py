"""Discover publisher-linked AI Singapore research cards, not global menus."""
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from src.core.exceptions import ScanError

ROOT = 'https://aisingapore.org/category/ai-research/'


def discover(source, scanner):
    queue, visited, urls = [source.url], set(), []
    while queue and len(visited) < source.max_listing_pages and len(urls) < source.max_articles_per_scan:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        if not scanner.is_allowed(url):
            if not urls:
                raise ScanError('AI Singapore research archive is not permitted')
            continue
        page = scanner.fetch_url(url, source.name)
        if not page.url.startswith(ROOT):
            raise ScanError('AI Singapore archive redirected away from research')
        soup = BeautifulSoup(page.html, 'lxml')
        for link in soup.select('main article h2 a[href]'):
            parsed = urlparse(urljoin(page.url, link['href']))
            candidate = parsed._replace(query='', fragment='').geturl()
            if (parsed.scheme == 'https' and parsed.netloc == 'aisingapore.org'
                    and len(parsed.path.strip('/').split('/')) == 1 and parsed.path.strip('/')
                    and candidate not in urls and scanner.is_allowed(candidate)):
                urls.append(candidate)
            if len(urls) >= source.max_articles_per_scan:
                break
        for link in soup.select('main .nav-links a[href]'):
            parsed = urlparse(urljoin(page.url, link['href']))
            candidate = parsed._replace(query='', fragment='').geturl()
            if (parsed.scheme == 'https' and parsed.netloc == 'aisingapore.org'
                    and re.fullmatch(r'/category/ai-research/page/\d+/', parsed.path)
                    and candidate not in visited and candidate not in queue):
                queue.append(candidate)
    return urls
