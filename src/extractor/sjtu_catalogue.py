"""Reviewed public SJTU programme list; preserve mixed-discipline scope."""
from bs4 import BeautifulSoup
from src.core.exceptions import ExtractionError

URL = 'https://isc.sjtu.edu.cn/kindeditor/Upload/file/20251124/20251124165651_6651.pdf'
TITLE = 'SJTU 2026 Chinese-taught undergraduate programme list (mixed disciplines)'


def catalogue_text(page):
    if page.url != URL or page.content_type != 'application/pdf':
        raise ExtractionError('SJTU catalogue response is not the reviewed PDF')
    body = BeautifulSoup(page.html, 'lxml').select_one('article')
    text = body.get_text('\n', strip=True) if body else ''
    normalised = ' '.join(text.split()).casefold()
    if len(text.split()) < 100 or not all(marker in normalised for marker in (
            '2026 sjtu undergraduate program', 'mechanical engineering', 'international students')):
        raise ExtractionError('SJTU programme catalogue text unavailable or insufficient')
    return ('Official programme list, not a full syllabus or competency framework. '
            'Mixed disciplines: includes non-STE programmes; downstream analysis must select STE-relevant entries. '
            'PDF table reading order may differ from the original; consult the linked PDF before assigning school, major or duration relationships.\n\n' + text)
