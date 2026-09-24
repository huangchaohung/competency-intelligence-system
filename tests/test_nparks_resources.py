from types import SimpleNamespace
import pytest
from src.scanner.nparks_resources import discover
from src.scanner.web_page_scanner import DownloadedPage
from src.models.domain import Source, SourceType
from src.extractor.article_extractor import ArticleExtractor
from src.core.exceptions import ExtractionError


def test_research_discovery_excludes_menus_anchors_and_external_links():
    url = 'https://www.nparks.gov.sg/services/research-programmes'
    html = '''<div class="header"><a href="/visit/activities/shopping">Shopping</a></div>
    <div class="main-body"><a href="#top">Top</a>
    <a href="/services/research-programmes/city-in-nature-research-programme">Research</a>
    <a href="/services/research-programmes/city-in-nature-research-programme#themes">Themes</a>
    <a href="https://other.example/course">Other</a><a href="/nature">Menu</a></div>'''
    scanner = SimpleNamespace(is_allowed=lambda u: True, fetch_url=lambda *a: DownloadedPage(url, html))
    assert discover(Source(1, 'Research', url, 'NParks'), scanner) == [url, url + '/city-in-nature-research-programme']


def test_strategy_is_one_standalone_page_and_body_preserves_accordion():
    url = 'https://www.nparks.gov.sg/who-we-are/city-in-nature-key-strategies'
    html = '<title>City in Nature</title><div class="header">MENU COOKIE</div><div class="main-body">' + '<p>Ecological connectivity restoration methods. </p>' * 30 + '<div class="accordion-body">Nature based solutions</div><a href="/nature">Nature</a></div>'
    page = DownloadedPage(url, html)
    source = Source(1, 'Strategies', url, 'NParks', source_type=SourceType.ARTICLE)
    assert discover(source, SimpleNamespace(is_allowed=lambda u: True, fetch_url=lambda *a: page)) == [url]
    evidence = ArticleExtractor().extract(page, source, 1)
    assert 'MENU COOKIE' not in evidence.article_text
    assert 'Nature based solutions' in evidence.article_text
    with pytest.raises(ExtractionError):
        ArticleExtractor().extract(DownloadedPage(url, '<div>Menu ' * 300), source, 1)
