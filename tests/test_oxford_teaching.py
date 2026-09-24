from dataclasses import replace
import pytest
from src.models.domain import Source, SourceType
from src.scanner.source_router import SourceRouter
from src.scanner.web_page_scanner import DownloadedPage
from src.core.exceptions import ScanError

ROOT = 'https://www.energy.ox.ac.uk/research/teaching-and-training/'
COURSE = 'https://www.ox.ac.uk/admissions/graduate/courses/msc-energy-systems'


def test_oxford_targets_actual_official_courses_with_permissions_and_cap():
    class Scanner:
        blocked = set()
        def is_allowed(self, url):
            return url not in self.blocked
        def fetch_url(self, url, name):
            return DownloadedPage(ROOT, f'''<article id="single_article">
            <a href="{COURSE}">MSc</a><a href="{COURSE}#details">Duplicate</a>
            <a href="/research/bioenergy/">Research menu</a>
            <a href="https://partner.example/course">Partner</a>
            <a href="https://www.ox.ac.uk.evil.example/admissions/graduate/courses/fake">Other</a>
            </article>''')
    scanner = Scanner()
    source = Source(1, 'Oxford', ROOT, 'Oxford', source_type=SourceType.CATALOGUE)
    router = SourceRouter(scanner)
    assert router.discover(source) == [ROOT, COURSE]
    assert router.discover(replace(source, max_articles_per_scan=1)) == [ROOT]
    scanner.blocked = {COURSE}
    assert router.discover(source) == [ROOT]
    scanner.blocked = {ROOT}
    with pytest.raises(ScanError):
        router.discover(source)
