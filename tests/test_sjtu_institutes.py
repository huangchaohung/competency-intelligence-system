import pytest
from src.extractor.sjtu_institutes import directory_text, URL
from src.extractor.article_extractor import ArticleExtractor
from src.scanner.web_page_scanner import DownloadedPage
from src.models.domain import Source
from src.core.exceptions import ExtractionError
from src.workflow.scan_workflow import ScanWorkflow


def test_research_hub_exclusion_preserves_detailed_directory():
    root = 'https://global.sjtu.edu.cn/en/research'
    assert ScanWorkflow._is_utility_url(root)
    assert ScanWorkflow._is_utility_url(root + '/')
    assert not ScanWorkflow._is_utility_url(URL)
    assert not ScanWorkflow._is_utility_url(root + '/academic-strengths')
    assert not ScanWorkflow._is_utility_url('https://other.example/en/research')


def test_directory_preserves_attribution_and_mixed_scope():
    html = '<nav>MENU</nav><div class="slide-door accordion"><div class="accordion-title"><div class="title">Institute A</div></div>'
    html += '<div class="accordion-content"><div class="mce-content-body">' + 'Urban research and public policy descriptions. ' * 20
    html += '<div class="info">CONTACT NOISE</div></div></div></div>'
    result = ArticleExtractor().extract(DownloadedPage(URL, html), Source(1, 'SJTU', URL, 'SJTU'), 1)
    assert 'Institute A' in result.article_text and 'public policy' in result.article_text
    assert 'CONTACT NOISE' not in result.article_text and 'MENU' not in result.article_text
    assert 'non-STE' in result.article_text and 'mixed disciplines' in result.title
    assert result.url == URL


def test_directory_missing_structure_is_not_navigation_fallback():
    with pytest.raises(ExtractionError):
        directory_text('<main>'+'Research descriptions. '*100+'</main>')
    with pytest.raises(ExtractionError):
        directory_text('<div class="slide-door accordion"><div class="accordion-content">Missing heading</div></div>')
