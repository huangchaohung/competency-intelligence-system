import pytest
from src.scanner.nus_curriculum import matches, fetch_curriculum
from src.scanner.source_router import SourceRouter
from src.models.domain import Source
from src.core.exceptions import ScanError

URL = 'https://cde.nus.edu.sg/arch/programmes/master-of-urban-planning/curriculum'


def test_nus_browser_scope_and_permission():
    assert matches(URL) and matches(URL + '/')
    assert not matches(URL + '?anything=1')
    assert not matches(URL.replace('cde.nus.edu.sg', 'other.example'))
    assert not matches(URL + '/other')
    class Scanner:
        def is_allowed(self, url):
            return False
    with pytest.raises(ScanError, match='not permitted'):
        fetch_curriculum(Scanner(), URL)


def test_nus_browser_discovers_curriculum_not_menu():
    class Scanner:
        def is_allowed(self, url):
            return True
    source = Source(1, 'NUS', URL, 'NUS', use_browser_rendering=True)
    assert SourceRouter(Scanner()).discover(source) == [URL]


def test_curriculum_body_keeps_courses_and_requirements_not_sidebar():
    from src.models.domain import SourceType
    from src.scanner.web_page_scanner import DownloadedPage
    from src.extractor.article_extractor import ArticleExtractor
    html = '''<title>Urban Planning</title><main id="main-container"><div class="template-b">
    <div class="col-md-3"><p>Faculty Admissions Contact Us</p></div>
    <div class="col-md-9"><h2>Curriculum</h2><p>Complete 80 Units.</p>
    <table><tr><td>DEP5113 Introduction to Urban Data Science</td><td>4 Units</td></tr>
    <tr><td>AR5301 Geographic Information System</td><td>4 Units</td></tr></table></div></div></main>'''
    source = Source(1, 'NUS', URL, 'NUS', source_type=SourceType.CATALOGUE)
    text = ArticleExtractor().extract(DownloadedPage(URL, html), source, 1).article_text
    assert 'Complete 80 Units' in text and 'DEP5113' in text and 'AR5301' in text
    assert 'Faculty Admissions' not in text
