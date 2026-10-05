"""Reviewed Harvard PLL course body, excluding suggested-course cards."""
from bs4 import BeautifulSoup
from src.core.exceptions import ExtractionError

URL = 'https://pll.harvard.edu/course/ai-strategy-business-leaders-hype-impact-0/2026-10-0'


def course_text(html):
    soup = BeautifulSoup(html, 'lxml')
    bodies = soup.select('.group-course-description .body.field--name-body')
    if len(bodies) != 1:
        raise ExtractionError('Harvard course description unavailable or ambiguous')
    body = bodies[0]
    for noise in body.select('script, style, nav, form, .field__label'):
        noise.decompose()
    text = body.get_text('\n', strip=True)
    if len(text.split()) < 15:
        raise ExtractionError('Harvard course description insufficient')
    return 'Published course description only; not a complete syllabus. Related-course suggestions omitted.\n\n' + text
