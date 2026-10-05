"""Reviewed SJTU programme overview sections, not admission instructions."""
from bs4 import BeautifulSoup
from src.core.exceptions import ExtractionError

URL = 'https://global.sjtu.edu.cn/en/study-sjtu/prospective/degree-programs/794'
HEADINGS = {'Programs Introduction', 'Sustainable Energy (SE)',
            'Health Science and Technology (HST)', 'International Opportunities', 'Industrial Experience'}
CIVIL_URL = 'https://global.sjtu.edu.cn/en/study-sjtu/prospective/degree-programs/778'
SUMMER_URL = 'https://global.sjtu.edu.cn/en/study-sjtu/prospective/non-degree-programs/522'
EXCHANGE_URL = 'https://global.sjtu.edu.cn/en/study-sjtu/prospective/non-degree-programs/281'
CLUSTER_LANGUAGES = {
    'https://global.sjtu.edu.cn/en/study-sjtu/prospective/degree-programs/278': 'English',
    'https://global.sjtu.edu.cn/en/study-sjtu/prospective/degree-programs/279': 'French',
}
TITLES = {
    URL: 'SJTU GIFT undergraduate programmes: Sustainable Energy and Health Science and Technology',
    CIVIL_URL: 'SJTU BEng in Civil Engineering (Smart and Sustainable Construction)',
    SUMMER_URL: 'SJTU Global Summer School overview (mixed disciplines)',
    EXCHANGE_URL: 'SJTU semester exchange: programmes and courses (mixed disciplines)',
}
TITLES.update({url: f'SJTU undergraduate Engineering Cluster ({language}-taught)'
               for url, language in CLUSTER_LANGUAGES.items()})
CIVIL_HEADINGS = {'Programme Introduction', 'What You’ll Study',
                  'Program Highlights and Career Prospects', 'Faculty and Facilities', 'Global Mobilities'}


def programme_text(html, url=URL):
    if url not in TITLES:
        raise ExtractionError('Unreviewed SJTU programme URL')
    allowed = CIVIL_HEADINGS if url == CIVIL_URL else HEADINGS
    soup = BeautifulSoup(html, 'lxml')
    if url == EXCHANGE_URL:
        return _exchange_text(soup)
    if url == SUMMER_URL:
        return _summer_text(soup)
    if url in CLUSTER_LANGUAGES:
        return _cluster_text(soup, CLUSTER_LANGUAGES[url])
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


def _cluster_text(soup, language):
    """These two reviewed pages have an unheaded programme-introduction block."""
    candidates = []
    for item in soup.select('.page-item'):
        if item.select_one('.title') is not None:
            continue
        for unwanted in item.select('script, style, nav, form'):
            unwanted.decompose()
        text = item.get_text('\n', strip=True)
        normalised = ' '.join(text.split()).casefold()
        if (f'engineering cluster program in {language.lower()}' in normalised
                and 'mechanical engineering' in normalised and len(text.split()) >= 100):
            candidates.append(text)
    if len(candidates) != 1:
        raise ExtractionError('SJTU cluster programme content block unavailable or ambiguous')
    return ('Selected public programme overview; not a complete syllabus. '
            'Admission and fee instructions omitted.\n\n' + candidates[0])


def _summer_text(soup):
    """Retain the reviewed unheaded overview, not site-wide navigation."""
    candidates = []
    for item in soup.select('.page-item'):
        if item.select_one('.title') is not None:
            continue
        for unwanted in item.select('script, style, nav, form'):
            unwanted.decompose()
        text = item.get_text('\n', strip=True)
        normalised = ' '.join(text.split()).casefold()
        if ('global summer school' in normalised and 'courses' in normalised
                and len(text.split()) >= 100):
            candidates.append(text)
    if len(candidates) != 1:
        raise ExtractionError('SJTU summer school overview unavailable or ambiguous')
    return ('Public summer-school overview with example courses, not a complete course catalogue or syllabus. '
            'Mixed disciplines: select STE-relevant courses for downstream analysis.\n\n' + candidates[0])


def _exchange_text(soup):
    candidates = []
    for item in soup.select('.page-item .mce-content-body > .slide-door'):
        for unwanted in item.select('script, style, nav, form'):
            unwanted.decompose()
        text = item.get_text('\n', strip=True)
        normalised = ' '.join(text.split())
        if normalised.startswith('3. PROGRAMS & COURSES') and len(text.split()) >= 100:
            candidates.append(text)
    if len(candidates) != 1:
        raise ExtractionError('SJTU exchange academic section unavailable or ambiguous')
    return ('Selected exchange programmes and courses section, including access restrictions; '
            'not a complete syllabus. Mixed disciplines: select STE-relevant entries. '
            'Linked course documents have not been retrieved in this record.\n\n' + candidates[0])
