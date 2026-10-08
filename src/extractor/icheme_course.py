"""Reviewed IChemE engineering course sections."""
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from src.core.exceptions import ExtractionError

PREFIX = '/training-events/training/courses-a-z/'
SLUGS = {
    'layer-of-protection-analysis-lopa', 'fundamentals-of-process-safety',
    'hazop-study-for-team-leaders-and-team-members',
    'practical-distillation-technology',
    'production-process-and-emergency-systems-on-oil-and-gas-installations',
    'human-factors-module-3',
}


def matches(url):
    parsed = urlparse(url)
    return (parsed.scheme == 'https' and parsed.netloc == 'www.icheme.org'
            and parsed.path.startswith(PREFIX)
            and parsed.path[len(PREFIX):].split('/')[0] in SLUGS)


def course_text(html):
    soup = BeautifulSoup(html, 'lxml')
    sections = []
    found = set()
    allowed = {'Overview', 'Learning outcomes', 'Who will benefit', 'Course outline'}
    for body in soup.select('main .umb-body'):
        active = False
        for child in body.children:
            if getattr(child, 'name', None) == 'h2':
                label = child.get_text(' ', strip=True)
                active = label in allowed
                if active:
                    found.add(label)
            if active and getattr(child, 'name', None) not in {'script', 'style', 'form'}:
                text = child.get_text(' ', strip=True) if hasattr(child, 'get_text') else str(child).strip()
                if text:
                    sections.append(text)
    text = '\n\n'.join(sections)
    if not {'Overview', 'Course outline'}.issubset(found) or len(text.split()) < 100:
        raise ExtractionError('IChemE academic course sections unavailable or insufficient')
    return ('Selected public course overview and outline; not full teaching materials. '
            'Testimonials and booking information omitted.\n\n' + text)
