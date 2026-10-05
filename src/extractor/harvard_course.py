"""Reviewed Harvard PLL course body, excluding suggested-course cards."""
from bs4 import BeautifulSoup
from src.core.exceptions import ExtractionError
from urllib.parse import urlparse

URL = 'https://pll.harvard.edu/course/ai-strategy-business-leaders-hype-impact-0/2026-10-0'


def matches(url):
    parsed = urlparse(url)
    return (parsed.scheme == 'https' and parsed.netloc == 'pll.harvard.edu'
            and parsed.path.startswith('/course/') and bool(parsed.path[len('/course/'):].strip('/')))


def course_text(html):
    soup = BeautifulSoup(html, 'lxml')
    bodies = soup.select('.group-course-description .body.field--name-body')
    if len(bodies) != 1:
        raise ExtractionError('Harvard course description unavailable or ambiguous')
    outcomes = soup.select('.group-course-description .field--name-field-course-nutshell')
    if len(outcomes) > 1:
        raise ExtractionError('Harvard course learning outcomes ambiguous')
    sections = []
    for label, fields in (("What you'll learn", outcomes), ('Course description', bodies)):
        for field in fields:
            for noise in field.select('script, style, nav, form, .field__label'):
                noise.decompose()
            content = field.get_text('\n', strip=True)
            if content:
                sections.append((label, content))
    text = '\n\n'.join(content for _, content in sections)
    if len(text.split()) < 15:
        raise ExtractionError('Harvard course description insufficient')
    return ('Published course description and available learning outcomes; not a complete syllabus. '
            'Related-course suggestions omitted.\n\n' + '\n\n'.join(label+'\n'+content for label, content in sections))
