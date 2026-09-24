from dataclasses import replace
from src.models.domain import Source
from src.scanner.source_router import SourceRouter
from src.scanner.web_page_scanner import DownloadedPage


def test_cuge_only_linked_government_pdfs_with_limits_and_permissions():
    root = 'https://cuge.nparks.gov.sg/resources/publications/'
    pdf = 'https://isomer-user-content.by.gov.sg/32/id/guide.pdf'
    class Scanner:
        def is_allowed(self, url):
            return 'denied' not in url
        def fetch_url(self, url, name):
            return DownloadedPage(root, f'''<a href="{pdf}">Guide</a>
                <a href="{pdf}#page=2">Duplicate</a>
                <a href="https://isomer-user-content.by.gov.sg/32/denied.pdf">Denied</a>
                <a href="https://isomer-user-content.by.gov.sg/99/other.pdf">Other collection</a>
                <a href="https://example.org/32/guide.pdf">External</a>
                <a href="https://isomer-user-content.by.gov.sg/32/id/index.html">Not PDF</a>''')
    source = Source(1, 'CUGE', root, 'NParks')
    assert SourceRouter(Scanner()).discover(source) == [root, pdf]
    assert SourceRouter(Scanner()).discover(replace(source, max_articles_per_scan=1)) == [root]
