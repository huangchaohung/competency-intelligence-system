from unittest.mock import Mock
from src.scanner.harvard_catalogue import discover, ROOT
from src.scanner.web_page_scanner import DownloadedPage
from src.models.domain import Source


def test_subject_discovery_balances_cards_and_respects_budget():
    scanner = Mock()
    scanner.is_allowed.return_value = True
    def fetch(url, name):
        subject = url.rsplit('/', 1)[-1]
        html = '<h3><a href="/course/navigation">Navigation</a></h3><div class="views-id-catalog">'
        html += ''.join(f'<h3><a href="/course/{subject}-{i}">Course</a></h3>' for i in range(3))
        return DownloadedPage(url, html+'</div>')
    scanner.fetch_url.side_effect = fetch
    source = Source(1, 'Harvard', ROOT, 'Harvard', max_listing_pages=2, max_articles_per_scan=3)
    result = discover(source, scanner)
    assert result == ['https://pll.harvard.edu/course/computer-science-0', 'https://pll.harvard.edu/course/data-science-0', 'https://pll.harvard.edu/course/computer-science-1']
    assert scanner.fetch_url.call_count == 2
