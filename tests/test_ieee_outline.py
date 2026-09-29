import pytest
from src.extractor.article_extractor import ArticleExtractor
from src.scanner.web_page_scanner import DownloadedPage
from src.models.domain import Source
from src.core.exceptions import ExtractionError

URL = 'https://resourcecenter.ieee-pes.org/education/tutorials/pes_ed_tut_02gest_042522_sld'


def test_reviewed_short_outline_keeps_sessions_and_disclaimer():
    text = ' '.join(f'Session {n} Energy storage technologies safety control applications practical engineering learning outcomes and integration.' for n in range(1,5))
    html = '<main><article><div class="field--name-body">'+text+'</div></article></main>'
    source = Source(1,'IEEE',URL,'IEEE')
    item = ArticleExtractor().extract(DownloadedPage(URL,html),source,1)
    assert 'full resource not retrieved' in item.article_text
    assert 'Session 4' in item.article_text
    with pytest.raises(ExtractionError):
        ArticleExtractor().extract(DownloadedPage(URL,html.replace('Session 4','Other')),source,1)
    with pytest.raises(ExtractionError):
        ArticleExtractor().extract(DownloadedPage(URL+'-other',html),source,1)
