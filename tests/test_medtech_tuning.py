from src.models.domain import Source
from src.scanner.source_router import SourceRouter
from src.scanner.web_page_scanner import DownloadedPage
from src.dashboard.source_configuration import EDITOR_COLUMNS, _sources_from_table
import pandas as pd


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
