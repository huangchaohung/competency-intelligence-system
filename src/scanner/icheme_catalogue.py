"""Public course-directory API observed in IChemE's listing script."""
import json
from urllib.parse import urljoin, urlparse
import requests
from src.core.exceptions import ScanError
from src.scanner.web_page_scanner import DEFAULT_HEADERS, MAX_RESPONSE_BYTES

ROOT = 'https://www.icheme.org/training-events/training/courses-a-z'
API = 'https://www.icheme.org/umbraco/api/coursesapi/SearchCoursesDirectory'


def discover(source, scanner):
    urls = []
    for page in range(1, source.max_listing_pages + 1):
        endpoint = API + f'?&searchText=&topics=&formats=&locations=&dateFrom=&dateTo=&take=12&page={page}'
        if not scanner.is_allowed(endpoint):
            raise ScanError('IChemE catalogue API discovery not permitted')
        try:
            with requests.get(endpoint, headers=DEFAULT_HEADERS, timeout=(5, 20), stream=True, allow_redirects=False) as response:
                if 300 <= response.status_code < 400:
                    raise ScanError('IChemE catalogue API redirected')
                response.raise_for_status()
                data = bytearray()
                for chunk in response.iter_content(8192):
                    data.extend(chunk)
                    if len(data) > MAX_RESPONSE_BYTES:
                        raise ScanError('IChemE catalogue response exceeds size limit')
                payload = json.loads(data)
        except (requests.RequestException, ValueError) as error:
            raise ScanError('IChemE catalogue API retrieval failed') from error
        if not isinstance(payload, dict) or not isinstance(payload.get('Courses'), list):
            raise ScanError('IChemE catalogue response has invalid course records')
        records = payload['Courses']
        if not records:
            break
        for record in records:
            if not isinstance(record, dict) or not isinstance(record.get('Url'), str):
                continue
            url = urljoin(ROOT, record['Url'])
            parsed = urlparse(url)
            url = parsed._replace(fragment='').geturl()
            if (parsed.scheme == 'https' and parsed.netloc == 'www.icheme.org'
                    and parsed.path.startswith('/training-events/training/courses-a-z/')
                    and parsed.path.rstrip('/') != urlparse(ROOT).path and not parsed.query
                    and url not in urls and scanner.is_allowed(url)):
                urls.append(url)
            if len(urls) >= source.max_articles_per_scan:
                return urls
        total = payload.get('TotalPageCount')
        if isinstance(total, int) and page >= total:
            break
    return urls
