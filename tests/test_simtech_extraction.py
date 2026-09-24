import pytest
from src.models.domain import Source, SourceType
from src.extractor.article_extractor import ArticleExtractor
from src.scanner.web_page_scanner import DownloadedPage
from src.core.exceptions import ExtractionError
from src.core.exceptions import ScanError
from src.scanner.source_router import SourceRouter

URL = 'https://www.a-star.edu.sg/simtech/research/sustainability-informatics-strategy-%28sis%29'


@pytest.mark.parametrize('url', [URL, URL.replace('%28', '(').replace('%29', ')')])
def test_simtech_single_resource_discovery(url):
    class Scanner:
        def is_allowed(self, candidate):
            return True
        def fetch_url(self, *args):
            raise AssertionError('Do not discover site navigation for standalone resource')
    source = Source(1, 'SIMTech', url, 'A*STAR', source_type=SourceType.RESEARCH)
    assert SourceRouter(Scanner()).discover(source) == [url]
    scanner = Scanner()
    scanner.is_allowed = lambda candidate: False
    with pytest.raises(ScanError):
        SourceRouter(scanner).discover(source)


def test_simtech_preserves_list_and_plain_text_without_navigation():
    source = Source(1, 'SIMTech', URL, 'A*STAR', source_type=SourceType.RESEARCH)
    text = 'Life Cycle Assessment and industrial symbiosis research. ' * 20
    html = '<main><nav>Corporate navigation</nav><div class="rich-text rte">' + text + '<ul><li>Operations Decarbonisation</li></ul></div></main>'
    evidence = ArticleExtractor().extract(DownloadedPage(URL, html), source, 1)
    assert 'Operations Decarbonisation' in evidence.article_text
    assert 'Corporate navigation' not in evidence.article_text
    assert evidence.evidence_type == 'RESEARCH_CAPABILITY'
    with pytest.raises(ExtractionError):
        ArticleExtractor().extract(DownloadedPage(URL, '<main>No research block</main>'), source, 1)
