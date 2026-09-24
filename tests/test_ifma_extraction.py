from src.extractor.article_extractor import ArticleExtractor
from src.models.domain import Source, SourceType
from src.scanner.web_page_scanner import DownloadedPage


def test_ifma_course_sections_survive_navigation_cleanup():
    url = 'https://www.ifma.org/professional-development/individual-courses/'
    source = Source(1, 'IFMA', url, 'IFMA', source_type=SourceType.CATALOGUE)
    html = '''<html><title>Individual courses</title><body>
    <header><nav><ul><li>Menu only</li></ul></nav></header>
    <section><h2>Operations and Maintenance</h2>
    <p>Learn to manage building systems and improve maintenance practices in facilities.</p></section>
    <footer>Footer only</footer></body></html>'''
    result = ArticleExtractor().extract(DownloadedPage(url, html), source, 1)
    assert 'Operations and Maintenance' in result.article_text
    assert 'building systems' in result.article_text
    assert 'Menu only' not in result.article_text
    assert 'Footer only' not in result.article_text
