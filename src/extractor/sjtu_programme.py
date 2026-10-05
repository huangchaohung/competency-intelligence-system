"""Reviewed SJTU programme overview sections, not admission instructions."""
from bs4 import BeautifulSoup
from src.core.exceptions import ExtractionError

URL = 'https://global.sjtu.edu.cn/en/study-sjtu/prospective/degree-programs/794'
HEADINGS = {'Programs Introduction', 'Sustainable Energy (SE)',
            'Health Science and Technology (HST)', 'International Opportunities', 'Industrial Experience'}
CIVIL_URL = 'https://global.sjtu.edu.cn/en/study-sjtu/prospective/degree-programs/778'
TITLES = {
    URL: 'SJTU GIFT undergraduate programmes: Sustainable Energy and Health Science and Technology',
    CIVIL_URL: 'SJTU BEng in Civil Engineering (Smart and Sustainable Construction)',
}
CIVIL_HEADINGS = {'Programme Introduction', 'What You’ll Study',
                  'Program Highlights and Career Prospects', 'Faculty and Facilities', 'Global Mobilities'}


def programme_text(html, url=URL):
    if url not in TITLES:
        raise ExtractionError('Unreviewed SJTU programme URL')
    allowed = CIVIL_HEADINGS if url == CIVIL_URL else HEADINGS
    soup = BeautifulSoup(html, 'lxml')
    sections = []
    headings = set()
    for item in soup.select('.page-item'):
        heading = item.select_one('.title')
        if heading is None or heading.get_text(' ', strip=True) not in allowed:
            continue
        headings.add(heading.get_text(' ', strip=True))
        for unwanted in item.select('script, style, nav, form'):
            unwanted.decompose()
        sections.append(item.get_text('\n', strip=True))
    text = '\n\n'.join(sections)
    required = {'Programme Introduction', 'What You’ll Study'} if url == CIVIL_URL else {'Programs Introduction'}
    markers = ('civil engineering', 'construction') if url == CIVIL_URL else ('sustainable energy', 'health')
    if (not required.issubset(headings) or len(text.split()) < 100
            or not all(marker in text.casefold() for marker in markers)):
        raise ExtractionError('SJTU programme content block unavailable or insufficient')
    return 'Selected public programme overview sections; not a complete syllabus. Admission and fee instructions omitted.\n\n' + text
