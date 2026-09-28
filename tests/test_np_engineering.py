from types import SimpleNamespace
import pytest
from src.scanner.np_engineering import ROOT, discover
from src.scanner.web_page_scanner import DownloadedPage
from src.models.domain import Source
from src.extractor.article_extractor import ArticleExtractor
from src.core.exceptions import ExtractionError


def test_discovery_scopes_deduplicates_and_limits_courses():
    a = ROOT + '/diploma-in-electrical-engineering'
    b = ROOT + '/common-engineering-programme'
    html = f'<a href="{ROOT}/diploma-in-outside">Outside</a><main><section id="full-time-courses">'
    html += ''.join(f'<a href="{u}">Course</a>' for u in [a,a+'#details',b,'https://other.example/diploma-in-test'])
    html += '</section></main>'
    scanner = SimpleNamespace(is_allowed=lambda u: True, fetch_url=lambda *a: DownloadedPage(ROOT,html))
    source = Source(1,'NP',ROOT,'NP',max_articles_per_scan=25)
    assert discover(source,scanner) == [a,b]
    from dataclasses import replace
    source = replace(source, max_articles_per_scan=1)
    assert discover(source,scanner) == [a]


def test_curriculum_keeps_module_text_not_marketing():
    url = ROOT + '/diploma-in-electrical-engineering'
    source = Source(1,'NP',ROOT,'NP')
    html = '<main><p>MARKETING</p><div id="what-you-will-learn"><h2>Modules</h2><p>'
    html += 'Electrical machines and circuit analysis. '*30 + '</p></div></main>'
    item = ArticleExtractor().extract(DownloadedPage(url,html),source,1)
    assert 'MARKETING' not in item.article_text
    assert 'circuit analysis' in item.article_text
    incomplete = html.replace('<h2>Modules</h2>', '<div data-slot="accordion-content"></div><h2>Modules</h2>')
    item = ArticleExtractor().extract(DownloadedPage(url,incomplete),source,1)
    assert 'some module details require interactive loading and were not retrieved' in item.article_text
    with pytest.raises(ExtractionError,match='curriculum unavailable'):
        ArticleExtractor().extract(DownloadedPage(url,'<main>Menu</main>'),source,1)
