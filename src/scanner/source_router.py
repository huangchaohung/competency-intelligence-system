"""Route configured sources to the smallest fitting discovery strategy."""
from src.models.domain import Source, SourceType
from src.scanner.article_discovery import ArticleDiscovery
from src.scanner.web_page_scanner import WebPageScanner
from urllib.parse import urlparse, urljoin, unquote
from bs4 import BeautifulSoup
from src.core.exceptions import ScanError


class SourceRouter:
    """Select the appropriate discovery strategy for each configured source."""
    def __init__(self, scanner: WebPageScanner) -> None:
        self._discovery = ArticleDiscovery(scanner)

    def discover(self, source: Source) -> list[str]:
        """Return candidate URLs using the strategy best suited to the source type."""
        parsed_source = urlparse(source.url)
        from src.extractor.sjtu_catalogue import URL as sjtu_catalogue_url
        if source.url == sjtu_catalogue_url:
            if not self._discovery._scanner.is_allowed(source.url):
                raise ScanError('SJTU catalogue retrieval is not permitted')
            return [source.url]
        from src.scanner.web_page_scanner import ICT_FRAMEWORK_URL
        if source.url == ICT_FRAMEWORK_URL:
            if not self._discovery._scanner.is_allowed(source.url):
                raise ScanError('ICT framework retrieval is not permitted')
            return [source.url]
        from src.scanner.imda_framework import matches as is_imda_framework, GENAI_PDF_URL
        if source.url == GENAI_PDF_URL:
            if not self._discovery._scanner.is_allowed(source.url):
                raise ScanError('IMDA GenAI document retrieval is not permitted')
            return [source.url]
        if is_imda_framework(source.url):
            if not self._discovery._scanner.is_allowed(source.url):
                raise ScanError('IMDA overview discovery is not permitted')
            return [source.url]
        if source.url.rstrip('/') == 'https://www.zju.edu.cn/english/sustainability/main.htm':
            import re
            scanner = self._discovery._scanner
            if not scanner.is_allowed(source.url):
                raise ScanError('Zhejiang sustainability discovery is not permitted')
            page = scanner.fetch_url(source.url, source.name)
            if page.url.rstrip('/') != source.url.rstrip('/'):
                raise ScanError('Zhejiang sustainability redirected away from the listing')
            urls = []
            for field in BeautifulSoup(page.html, 'lxml').select('span.url'):
                parsed = urlparse(urljoin(page.url, field.get_text(strip=True)))
                candidate = parsed._replace(fragment='').geturl()
                if (parsed.scheme == 'https' and parsed.netloc == 'www.zju.edu.cn'
                        and re.fullmatch(r'/english/\d{4}/\d{4}/c\d+a\d+/page\.psp', parsed.path)
                        and not parsed.query and candidate not in urls and scanner.is_allowed(candidate)):
                    urls.append(candidate)
                if len(urls) >= source.max_articles_per_scan:
                    break
            return urls
        if (parsed_source.hostname == 'www.ntu.edu.sg' and unquote(parsed_source.path).rstrip('/') ==
                '/engineering/coe-programmes/graduate/coe-programme-detail/master-of-science-(robotics-and-intelligent-systems)'):
            if not self._discovery._scanner.is_allowed(source.url):
                raise ScanError('NTU robotics programme is not permitted')
            return [source.url]
        if source.url.rstrip('/') == 'https://resourcecenter.ieee-pes.org/education/tutorials/pes_ed_tut_02gest_042522_sld':
            if not self._discovery._scanner.is_allowed(source.url):
                raise ScanError('IEEE storage tutorial is not permitted')
            return [source.url]
        from src.scanner.aisg_research import ROOT as aisg_root, discover as discover_aisg
        if source.url.rstrip('/') == aisg_root.rstrip('/'):
            return discover_aisg(source, self._discovery._scanner)
        from src.scanner.np_engineering import matches as is_np_engineering, discover as discover_np
        if is_np_engineering(source.url):
            return discover_np(source, self._discovery._scanner)
        from src.scanner.structured_pages import body_selector
        if body_selector(source.url):
            if not self._discovery._scanner.is_allowed(source.url):
                raise ScanError('Structured resource discovery is not permitted')
            if parsed_source.hostname in {'www.ice.org.uk', 'ice.org.uk'} and parsed_source.path.rstrip('/') == '/attributes':
                canonical = 'https://www.ice.org.uk/join-ice/attributes-for-professionally-qualified-membership'
                if not self._discovery._scanner.is_allowed(canonical):
                    raise ScanError('ICE canonical attributes page is not permitted')
                return [canonical]
            return [source.url]
        if source.url.rstrip('/') == 'https://programs.isa.org/ic32-cyber-training':
            if not self._discovery._scanner.is_allowed(source.url):
                raise ScanError('ISA course description is not permitted')
            return [source.url]
        if source.url == 'https://learning.energyinst.org/course/index.php':
            from urllib.parse import parse_qs
            scanner = self._discovery._scanner
            if not scanner.is_allowed(source.url):
                raise ScanError('Energy Institute catalogue is not permitted')
            page = scanner.fetch_url(source.url, source.name)
            urls = []
            # Verified public technical categories. Exclude staff, test, bespoke,
            # volunteer, assessment/resit and policy/admin destinations.
            categories = {'52', '1', '6', '10', '32', '34', '36', '40', '41'}
            for link in BeautifulSoup(page.html, 'lxml').select('a[href]'):
                parsed = urlparse(urljoin(page.url, link['href']))
                if (parsed.scheme == 'https' and parsed.netloc == 'learning.energyinst.org'
                        and parsed.path == '/course/index.php'
                        and parse_qs(parsed.query).get('categoryid', []) in [[value] for value in categories]):
                    url = parsed._replace(fragment='').geturl()
                    if url not in urls and scanner.is_allowed(url):
                        urls.append(url)
                    if len(urls) >= source.max_articles_per_scan:
                        break
            return urls
        from src.scanner.nparks_resources import matches as is_nparks_resource, discover as discover_nparks
        if is_nparks_resource(source.url):
            return discover_nparks(source, self._discovery._scanner)
        from src.scanner.nus_curriculum import matches as is_nus_curriculum
        if source.use_browser_rendering and is_nus_curriculum(source.url):
            if not self._discovery._scanner.is_allowed(source.url):
                raise ScanError('NUS curriculum discovery is not permitted')
            return [source.url]
        if source.url.rstrip('/') == 'https://www.energy.ox.ac.uk/research/teaching-and-training':
            scanner = self._discovery._scanner
            if not scanner.is_allowed(source.url):
                raise ScanError('Oxford teaching discovery is not permitted')
            page = scanner.fetch_url(source.url, source.name)
            urls = [source.url]
            content = BeautifulSoup(page.html, 'lxml').select_one('article#single_article')
            if content is not None:
                for link in content.select('a[href]'):
                    parsed = urlparse(urljoin(page.url, link['href']))
                    url = parsed._replace(fragment='').geturl()
                    if len(urls) >= source.max_articles_per_scan:
                        break
                    # Only actually linked official graduate course pages;
                    # exclude research navigation, profiles and partner sites.
                    if (parsed.scheme == 'https' and parsed.netloc == 'www.ox.ac.uk'
                            and parsed.path.startswith('/admissions/graduate/courses/')
                            and parsed.path.removeprefix('/admissions/graduate/courses/').strip('/')
                            and not parsed.query and url not in urls and scanner.is_allowed(url)):
                        urls.append(url)
            return urls
        if (parsed_source.hostname == 'www.a-star.edu.sg'
                and unquote(parsed_source.path).lower().rstrip('/') == '/simtech/research/sustainability-informatics-strategy-(sis)'):
            # This is a standalone research summary, not a listing. Its content
            # block has no onward resource links; global menus create noise and
            # encoded/unencoded duplicates of the same evidence.
            if not self._discovery._scanner.is_allowed(source.url):
                raise ScanError('SIMTech research discovery is not permitted')
            return [source.url]
        if (parsed_source.hostname == 'www.a-star.edu.sg'
                and parsed_source.path.lower().rstrip('/') == '/research/medical-technologies'):
            scanner = self._discovery._scanner
            if not scanner.is_allowed(source.url):
                raise ScanError('A*STAR MedTech discovery is not permitted')
            page = scanner.fetch_url(source.url, source.name)
            urls = [page.url]
            for link in BeautifulSoup(page.html, 'lxml').select('a[href]'):
                parsed = urlparse(urljoin(page.url, link['href']))
                url = parsed._replace(fragment='').geturl()
                if len(urls) >= source.max_articles_per_scan:
                    break
                if (parsed.scheme == 'https' and parsed.hostname == 'www.a-star.edu.sg'
                        and parsed.path.lower().rstrip('/') in {
                            '/research/medical-technologies/innovation-pillars',
                            '/research/medical-technologies/enablers'}
                        and not parsed.query and url not in urls and scanner.is_allowed(url)):
                    urls.append(url)
            return urls
        if source.url.rstrip('/') == 'https://cuge.nparks.gov.sg/resources/publications':
            scanner = self._discovery._scanner
            if not scanner.is_allowed(source.url):
                raise ScanError('CUGE publications discovery is not permitted')
            page = scanner.fetch_url(source.url, source.name)
            urls = [source.url]
            for link in BeautifulSoup(page.html, 'lxml').select('a[href]'):
                parsed = urlparse(urljoin(page.url, link['href']))
                url = parsed._replace(fragment='').geturl()
                if len(urls) >= source.max_articles_per_scan:
                    break
                if (parsed.scheme == 'https' and parsed.netloc == 'isomer-user-content.by.gov.sg'
                        and parsed.path.startswith('/32/') and parsed.path.lower().endswith('.pdf')
                        and not parsed.query and url not in urls and scanner.is_allowed(url)):
                    urls.append(url)
            return urls
        if source.url.rstrip('/') == 'https://www.nasa.gov/reference/systems-engineering-handbook':
            scanner = self._discovery._scanner
            if not scanner.is_allowed(source.url):
                raise ScanError('NASA handbook discovery is not permitted')
            page = scanner.fetch_url(source.url, source.name)
            soup = BeautifulSoup(page.html, 'lxml')
            paths = {'/reference/' + slug + '/' for slug in (
                '1-0-introduction', '2-0-fundamentals-of-systems-engineering',
                '3-0-nasa-program-project-life-cycle', '4-0-system-design-processes',
                '5-0-product-realization', '6-0-crosscutting-technical-management',
                'system-engineering-handbook-appendix')}
            urls = [source.url]
            for link in soup.select('a[href]'):
                parsed = urlparse(urljoin(page.url, link['href']))
                url = parsed._replace(fragment='').geturl()
                if len(urls) >= source.max_articles_per_scan:
                    break
                if (parsed.scheme == 'https' and parsed.netloc == 'www.nasa.gov'
                        and parsed.path in paths and not parsed.query
                        and url not in urls and scanner.is_allowed(url)):
                    urls.append(url)
            return urls
        if source.url.rstrip('/') == 'https://ocw.mit.edu':
            scanner = self._discovery._scanner
            if not scanner.is_allowed(source.url):
                raise ScanError('OCW discovery is not permitted')
            page = scanner.fetch_url(source.url, source.name)
            soup = BeautifulSoup(page.html, 'lxml')
            urls = []
            for card in soup.select('.course-card'):
                topics = {a.get_text(strip=True) for a in card.select('.course-card-topics a')}
                if not topics.intersection({'Science', 'Engineering', 'Mathematics', 'Energy', 'Health and Medicine'}):
                    continue
                link = card.select_one('.course-card-title a[href]')
                if not link:
                    continue
                url = urljoin(page.url, link['href'])
                parsed = urlparse(url)
                if (parsed.scheme == 'https' and parsed.netloc == 'ocw.mit.edu'
                        and len(parsed.path.strip('/').split('/')) == 2
                        and parsed.path.startswith('/courses/') and not parsed.query
                        and url not in urls and scanner.is_allowed(url)):
                    urls.append(url)
                if len(urls) >= source.max_articles_per_scan:
                    break
            if not urls:
                raise ScanError('No permitted STE course cards found on OCW')
            return urls
        if source.source_type in {SourceType.FRAMEWORK, SourceType.CATALOGUE}:
            return self._discovery.discover_resources(source)
        # A configured research resource can itself hold the evidence. Keep its
        # research classification rather than pretending it is a course catalogue.
        if source.source_type == SourceType.RESEARCH or (source.source_type == SourceType.ARTICLE and source.evidence_label.strip().lower() == 'research / report'):
            return self._discovery.discover_resources(source)
        if source.source_type == SourceType.INDEX:
            return self._discovery.discover_index(source)
        if source.source_type == SourceType.TREND:
            return self._discovery.discover_trend(source)
        return self._discovery.discover(source)
