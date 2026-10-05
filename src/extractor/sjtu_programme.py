"""Reviewed GIFT programme overview sections, not admission instructions."""
from bs4 import BeautifulSoup
from src.core.exceptions import ExtractionError

URL = 'https://global.sjtu.edu.cn/en/study-sjtu/prospective/degree-programs/794'
HEADINGS = {'Programs Introduction', 'Sustainable Energy (SE)',
            'Health Science and Technology (HST)', 'International Opportunities', 'Industrial Experience'}


def programme_text(html):
    soup = BeautifulSoup(html, 'lxml')
    sections = []
    headings = set()
    for item in soup.select('.page-item'):
        heading = item.select_one('.title')
        if heading is None or heading.get_text(' ', strip=True) not in HEADINGS:
            continue
        headings.add(heading.get_text(' ', strip=True))
        for unwanted in item.select('script, style, nav, form'):
            unwanted.decompose()
        sections.append(item.get_text('\n', strip=True))
    text = '\n\n'.join(sections)
    if ('Programs Introduction' not in headings or len(text.split()) < 100
            or 'sustainable energy' not in text.casefold() or 'health' not in text.casefold()):
        raise ExtractionError('SJTU programme content block unavailable or insufficient')
    return 'Selected public programme overview sections; not a complete syllabus. Admission and fee instructions omitted.\n\n' + text
