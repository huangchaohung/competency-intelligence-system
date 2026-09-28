from types import SimpleNamespace
import pytest
from src.scanner.source_router import SourceRouter
from src.scanner.web_page_scanner import DownloadedPage
from src.extractor.article_extractor import ArticleExtractor
from src.models.domain import Source, SourceType
from src.core.exceptions import ExtractionError


def test_energy_catalogue_excludes_staff_tests_and_policy():
    url = 'https://learning.energyinst.org/course/index.php'
    html = ''.join(f'<a href="{url}?categoryid={i}">Category</a>' for i in [52,11,28,37,6,52])
    html += '<a href="/admin/tool/policy/view.php">Privacy</a>'
    scanner = SimpleNamespace(is_allowed=lambda u: True, fetch_url=lambda *a: DownloadedPage(url, html))
    assert SourceRouter(scanner).discover(Source(1,'EI',url,'EI')) == [url+'?categoryid=52',url+'?categoryid=6']


def test_isa_title_only_is_not_course_evidence():
    url = 'https://www.isa.org/products/using-the-isa-iec-62443-standards-to-secure-your-c'
    source = Source(1,'ISA',url,'ISA',source_type=SourceType.CATALOGUE)
    page = DownloadedPage(url,'<main><h1>Using the ISA IEC 62443 Standards to Secure Your Control Systems</h1></main>')
    with pytest.raises(ExtractionError,match='title'):
        ArticleExtractor().extract(page,source,1)


def test_isa_description_keeps_outcomes_without_header():
    url = 'https://programs.isa.org/ic32-cyber-training'
    source = Source(1,'ISA',url,'ISA',source_type=SourceType.CATALOGUE)
    html = '<header>UNRELATED MENU</header><main class="body-container-wrapper"><h1>IC32</h1><p>Learn risk analysis and security management for industrial control systems.</p><ul><li>Understand defense in depth and zone conduit models</li></ul></main>'
    evidence = ArticleExtractor().extract(DownloadedPage(url,html),source,1)
    assert 'UNRELATED MENU' not in evidence.article_text
    assert 'defense in depth' in evidence.article_text
