from bs4 import BeautifulSoup
from src.extractor.article_extractor import ArticleExtractor
from src.scanner.article_discovery import ArticleDiscovery


def test_catalogue_preserves_course_names_rows_and_learning_outcomes():
    soup = BeautifulSoup('<nav>Shopping</nav><main><h1>Curriculum</h1><table><tr><td>SE 101</td><td><a href="/search?q=101">Systems Design</a></td></tr></table><h2>Outcomes</h2><ul><li>Evaluate interacting systems</li><li>Model engineering constraints</li></ul></main>', 'lxml')
    text = ArticleExtractor._extract_catalogue_text(soup)
    assert 'SE 101 Systems Design' in text
    assert 'Evaluate interacting systems' in text
    assert 'Model engineering constraints' in text
    assert '/search' not in text
    assert 'Shopping' not in text


def test_discovery_excludes_site_menu_links():
    soup = BeautifulSoup('<nav><a href="/shopping">Shop</a></nav><main><a href="/course">Course</a></main>', 'lxml')
    assert [a['href'] for a in ArticleDiscovery._article_links(soup)] == ['/course']
