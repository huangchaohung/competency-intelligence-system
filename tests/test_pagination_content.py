from bs4 import BeautifulSoup
from src.scanner.article_discovery import ArticleDiscovery


def test_feedback_url_is_not_pagination():
    soup = BeautifulSoup('<a href="/form/page-feedback?page=https://www.nist.gov/programs">Feedback</a><a href="/programs?page=2">2</a><a href="/news/next-generation">Next generation</a>', 'lxml')
    assert ArticleDiscovery._pagination_links(soup, 'https://www.nist.gov/programs', 'www.nist.gov') == ['https://www.nist.gov/programs?page=2']
