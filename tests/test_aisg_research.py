from types import SimpleNamespace
from src.scanner.aisg_research import ROOT, discover
from src.scanner.web_page_scanner import DownloadedPage
from src.models.domain import Source


def test_research_cards_pagination_caps_and_permissions():
    fetched = []
    def fetch(url, name):
        fetched.append(url)
        slug = 'one' if url == ROOT else 'two'
        html = '<main><nav><a href="/about/">About</a></nav>'
        html += f'<article><h2><a href="/{slug}/?utm_source=test">Title</a></h2></article>'
        html += '<article><h2><a href="https://connect.aisingapore.org/old/">Old</a></h2></article>'
        html += '<article><h2><a href="/blocked/">Blocked</a></h2></article>'
        html += '<div class="nav-links"><a href="/category/ai-research/page/2/?utm_source=test">2</a></div></main>'
        return DownloadedPage(url,html)
    scanner = SimpleNamespace(fetch_url=fetch,is_allowed=lambda u: '/blocked/' not in u)
    source = Source(1,'AISG',ROOT,'AISG',max_listing_pages=2,max_articles_per_scan=25)
    assert discover(source,scanner) == ['https://aisingapore.org/one/','https://aisingapore.org/two/']
    assert fetched == [ROOT, ROOT+'page/2/']
    from dataclasses import replace
    fetched.clear()
    assert discover(replace(source,max_articles_per_scan=1),scanner) == ['https://aisingapore.org/one/']
    assert fetched == [ROOT]
