from unittest.mock import Mock
from src.scanner.harvard_catalogue import discover, ROOT
from src.scanner.web_page_scanner import DownloadedPage
from src.models.domain import Source
from src.core.exceptions import ScanError
import pytest


def test_pagination_skips_page_zero_and_fragment_duplicates():
    scanner = Mock()
    scanner.is_allowed.return_value = True
    def fetch(url, name):
        html = '<div class="views-id-catalog"><h3><a href="/course/shared#one">Course</a></h3><h3><a href="/course/shared#two">Course</a></h3></div>'
        html += '<div class="pager"><a href="?page=0">First</a><a href="?page=1">Next</a><a href="https://other.example/?page=2">Outside</a></div>'
        return DownloadedPage(url, html)
    scanner.fetch_url.side_effect = fetch
    result = discover(Source(1, 'Harvard', ROOT, 'Harvard', max_listing_pages=6), scanner)
    requested = [call.args[0] for call in scanner.fetch_url.call_args_list]
    assert len(requested) == 6
    assert requested[-1] == 'https://pll.harvard.edu/subject/computer-science?page=1'
    assert not any('page=0' in url or 'other.example' in url for url in requested)
    assert result == ['https://pll.harvard.edu/course/shared']


def test_partial_subject_failure_keeps_successful_results_and_logs(caplog):
    scanner = Mock()
    scanner.is_allowed.return_value = True
    scanner.fetch_url.side_effect = [ScanError('Timeout'), DownloadedPage('https://pll.harvard.edu/subject/data-science', '<div class="views-id-catalog"><h3><a href="/course/data">Data</a></h3></div>')]
    source = Source(1, 'Harvard', ROOT, 'Harvard', max_listing_pages=2)
    assert discover(source, scanner) == ['https://pll.harvard.edu/course/data']
    assert 'subject listing skipped' in caplog.text
    scanner.fetch_url.side_effect = ScanError('Timeout')
    with pytest.raises(ScanError, match='Timeout'):
        discover(source, scanner)


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
