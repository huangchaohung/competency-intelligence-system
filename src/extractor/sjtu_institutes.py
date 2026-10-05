"""Extract the reviewed mixed-discipline directory without asserting STE relevance."""
from bs4 import BeautifulSoup
from src.core.exceptions import ExtractionError

URL = 'https://global.sjtu.edu.cn/en/research/institutions'
TITLE = 'SJTU research and think-tank directory (mixed disciplines)'


def directory_text(html):
    soup = BeautifulSoup(html, 'lxml')
    sections = []
    for block in soup.select('.slide-door.accordion'):
        heading = block.select_one('.accordion-title .title')
        body = block.select_one('.accordion-content .mce-content-body')
        if heading is None or body is None:
            raise ExtractionError('SJTU institute directory section incomplete')
        for noise in body.select('.info, script, style, nav, form'):
            noise.decompose()
        label = heading.get_text(' ', strip=True)
        text = body.get_text('\n', strip=True)
        if not label or not text:
            raise ExtractionError('SJTU institute directory section empty')
        sections.append(label + '\n' + text)
    text = '\n\n'.join(sections)
    if not sections or len(text.split()) < 100:
        raise ExtractionError('SJTU institute directory body unavailable')
    return ('Mixed-discipline research and think-tank directory, including non-STE policy and social-science entries. '
            'Not an explicit competency framework or course catalogue. Assess STE relevance individually; '
            'institution descriptions do not establish specific course offerings.\n\n' + text)
