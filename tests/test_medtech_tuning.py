from src.models.domain import Source
from src.scanner.source_router import SourceRouter
from src.scanner.web_page_scanner import DownloadedPage
from src.dashboard.source_configuration import EDITOR_COLUMNS, _sources_from_table
import pandas as pd
import pytest
from src.extractor.article_extractor import ArticleExtractor
from src.core.exceptions import ExtractionError


def test_medtech_short_overview_requires_all_named_enablers():
    url = 'https://www.a-star.edu.sg/research/medical-technologies/enablers'
    source = Source(1, 'MedTech', url, 'A*STAR')
    text = ('Research and development from laboratory to market supports innovative technological solutions. ' * 4
            + 'Needs-Based Innovation Talent Development Streamlined Funding and Evaluation '
              'Market Access and Implementation National Platforms')
    html = '<nav>OUTSIDE</nav><section class="page-content__inner">'+text+'</section>'
    result = ArticleExtractor().extract(DownloadedPage(url, html), source, 1)
    assert 'overview only' in result.article_text
    assert 'OUTSIDE' not in result.article_text
    with pytest.raises(ExtractionError, match='Insufficient'):
        ArticleExtractor().extract(DownloadedPage(url, html.replace('National Platforms', 'Other')), source, 1)
    with pytest.raises(ExtractionError, match='block unavailable'):
        ArticleExtractor().extract(DownloadedPage(url, '<main>'+text+'</main>'), source, 1)


def test_medtech_discovery_excludes_general_links():
    root = 'https://www.a-star.edu.sg/Research/medical-technologies'
    class Scanner:
        def is_allowed(self, url):
            return not url.endswith('enablers')
        def fetch_url(self, url, name):
            return DownloadedPage(root, '''<a href="/research">General research</a>
            <a href="/Research/medical-technologies/innovation-pillars">Pillars</a>
            <a href="/Research/medical-technologies/enablers">Enablers</a>
            <a href="https://other.example/Research/medical-technologies/innovation-pillars">Other</a>''')
    assert SourceRouter(Scanner()).discover(Source(1, 'MedTech', root, 'A*STAR')) == [
        root, 'https://www.a-star.edu.sg/Research/medical-technologies/innovation-pillars']


def test_simplified_editor_preserves_hidden_metadata():
    old = Source(1, 'Source', 'https://example.org', 'Org', country='Singapore',
                 category='Research', evidence_label='research / report')
    assert not {'Country', 'Category', 'Evidence label'}.intersection(EDITOR_COLUMNS)
    row = {'_key': 'id:1', 'Name': 'Edited', 'Discovery URL': old.url, 'Organisation': 'Org'}
    new = _sources_from_table([old], pd.DataFrame([row]))[0]
    assert (new.country, new.category, new.evidence_label) == (old.country, old.category, old.evidence_label)
