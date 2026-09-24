from dataclasses import replace
import pytest
from src.models.domain import Source, SourceType
from src.scanner.source_router import SourceRouter
from src.scanner.web_page_scanner import DownloadedPage
from src.extractor.article_extractor import ArticleExtractor
from src.core.exceptions import ExtractionError


def test_nasa_only_linked_handbook_chapters():
    root = 'https://www.nasa.gov/reference/systems-engineering-handbook'
    chapter = 'https://www.nasa.gov/reference/1-0-introduction/'
    class Scanner:
        def is_allowed(self, url):
            return 'appendix' not in url
        def fetch_url(self, url, name):
            return DownloadedPage(root, f'<a href="{chapter}">Intro</a><a href="{chapter}#x">Duplicate</a><a href="/news/media-contacts/">Contacts</a><a href="/reference/astronaut-fact-book/">Other reference</a><a href="/reference/system-engineering-handbook-appendix/">Appendix</a>')
    source = Source(1, 'NASA', root, 'NASA', source_type=SourceType.FRAMEWORK)
    assert SourceRouter(Scanner()).discover(source) == [root, chapter]
    assert SourceRouter(Scanner()).discover(replace(source, max_articles_per_scan=1)) == [root]


def test_login_content_rejected_without_rejecting_article_about_login():
    source = Source(1, 'ISEP', 'https://example.org/skills', 'ISEP')
    page = DownloadedPage(source.url, '<title>Member Login - ISEP</title><main>Login or Register. Activate account.</main>')
    with pytest.raises(ExtractionError, match='Login page'):
        ArticleExtractor().extract(page, source, 1)
    text = 'Digital engineering improves government authentication and services. ' * 30
    article = DownloadedPage(source.url, f'<title>From company chop to a single login</title><article><p>{text}</p></article>')
    assert ArticleExtractor().extract(article, source, 1).article_text


def test_nasa_framework_does_not_include_global_navigation():
    source = Source(1, 'NASA', 'https://www.nasa.gov/reference/systems-engineering-handbook', 'NASA', source_type=SourceType.FRAMEWORK)
    page = DownloadedPage(source.url, '<title>Handbook</title><div>Unrelated navigation</div><main><p>System design requires requirements analysis verification validation and technical management.</p></main>')
    result = ArticleExtractor().extract(page, source, 1)
    assert 'Unrelated navigation' not in result.article_text
