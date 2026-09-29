from types import SimpleNamespace
import pytest
from src.scanner.source_router import SourceRouter
from src.scanner.web_page_scanner import DownloadedPage
from src.extractor.article_extractor import ArticleExtractor
from src.models.domain import Source, SourceType
from src.core.exceptions import ExtractionError, ScanError


@pytest.mark.parametrize('url,body,kind', [
    ('https://www.a-star.edu.sg/simtech/kto/industrial-automation',
     '<main><div class="rich-text rte block">{}</div><div>OUTSIDE MENU</div></main>', SourceType.CATALOGUE),
    ('https://www.polimi.it/en/education/laurea-programmes/programme-detail/building-engineering-for-sustainability',
     '<main id="page-content">{}</main>', SourceType.CATALOGUE),
    ('https://www.polimi.it/en/education/laurea-magistrale-programmes/programme-detail/civil-engineering',
     '<main id="page-content">{}</main>', SourceType.CATALOGUE),
    ('https://www.ice.org.uk/join-ice/attributes-for-professionally-qualified-membership',
     '<main class="main-landing"><div class="accordion-tabs">{}</div><p>OUTSIDE MENU</p></main>', SourceType.FRAMEWORK),
    ('https://sust.hkust.edu.hk/students/sustainability-education',
     '<main><article class="node">{}</article></main>', SourceType.CATALOGUE),
])
def test_structured_overview_keeps_tabs_and_tables_not_navigation(url, body, kind):
    source = Source(1, 'Resource', url, 'Organisation', source_type=kind)
    scanner = SimpleNamespace(is_allowed=lambda u: True)
    assert SourceRouter(scanner).discover(source) == [url]
    content = '<div hidden>Competence attribute</div><table><tr><td>Curriculum credit</td></tr></table>'
    content += '<p>' + 'Engineering learning outcomes. ' * 40 + '</p>'
    html = '<nav>OUTSIDE MENU</nav>' + body.format(content)
    result = ArticleExtractor().extract(DownloadedPage(url, html), source, 1)
    assert 'OUTSIDE MENU' not in result.article_text
    assert 'Competence attribute' in result.article_text
    assert 'Curriculum credit' in result.article_text
    with pytest.raises(ExtractionError, match='body unavailable'):
        ArticleExtractor().extract(DownloadedPage(url, '<nav>menu</nav>'), source, 1)
    with pytest.raises(ExtractionError, match='redirected'):
        ArticleExtractor().extract(DownloadedPage('https://example.org/login', html), source, 1)
    with pytest.raises(ScanError, match='not permitted'):
        SourceRouter(SimpleNamespace(is_allowed=lambda u: False)).discover(source)


def test_ice_alias_uses_same_canonical_url_and_checks_permission():
    canonical = 'https://www.ice.org.uk/join-ice/attributes-for-professionally-qualified-membership'
    source = Source(1, 'ICE', 'https://www.ice.org.uk/attributes', 'ICE')
    assert SourceRouter(SimpleNamespace(is_allowed=lambda u: True)).discover(source) == [canonical]
    with pytest.raises(ScanError, match='not permitted'):
        SourceRouter(SimpleNamespace(is_allowed=lambda u: u != canonical)).discover(source)
