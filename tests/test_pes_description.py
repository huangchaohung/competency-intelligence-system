import pytest
from src.extractor.article_extractor import ArticleExtractor
from src.models.domain import Source
from src.scanner.web_page_scanner import DownloadedPage
from src.core.exceptions import ExtractionError


def test_pes_div_description_is_preserved_without_paid_controls():
    url = 'https://resourcecenter.ieee-pes.org/conferences/example/tutorial'
    source = Source(1, 'PES', url, 'IEEE PES')
    text = 'Study distributed energy integration control systems and reliability engineering. ' * 15
    html = f'<title>Tutorial</title><main><article><div>Sign in to buy</div><article><div class="field--name-body">{text}<br/>Learning outcomes include grid automation.</div></article><div>Related product unrelated</div></article></main>'
    result = ArticleExtractor().extract(DownloadedPage(url, html), source, 1)
    assert text.strip() in result.article_text
    assert 'Learning outcomes' in result.article_text
    assert 'full resource not retrieved' in result.article_text
    assert 'Sign in' not in result.article_text
    assert 'Related product' not in result.article_text
    assert result.title.endswith('[Public resource description]')


@pytest.mark.parametrize('body', ['', '<div class="field--name-body">Sign in to download.</div>'])
def test_pes_missing_or_short_description_is_not_evidence(body):
    url = 'https://resourcecenter.ieee-pes.org/publications/example'
    with pytest.raises(ExtractionError, match='public resource description'):
        ArticleExtractor().extract(DownloadedPage(url, f'<main><article>{body}</article></main>'), Source(1, 'PES', url, 'IEEE PES'), 1)
