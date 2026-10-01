"""Page-bounded records for one reviewed ICT PDF; not semantic table parsing."""
import re
from datetime import datetime
from bs4 import BeautifulSoup
from src.core.exceptions import ExtractionError
from src.models.domain import Evidence, EvidenceType
from src.scanner.web_page_scanner import ICT_FRAMEWORK_URL


def extract_sections(page, source, run_id):
    if page.url != ICT_FRAMEWORK_URL or page.content_type != 'application/pdf':
        raise ExtractionError('ICT framework is not the reviewed PDF')
    blocks = BeautifulSoup(page.html, 'lxml').select('article > p')
    groups = {}
    previous = 0
    for block in blocks:
        text = block.get_text('\n', strip=True)
        match = re.match(r'^\[PDF page (\d+)\]\s*', text)
        if not match:
            raise ExtractionError('ICT framework page reference missing')
        number = int(match[1])
        if not previous < number <= 600:
            raise ExtractionError('ICT framework page references invalid')
        previous = number
        groups.setdefault((number - 1) // 50, []).append((number, text))
    if not groups or len(groups) > source.max_articles_per_scan:
        raise ExtractionError('ICT framework sections exceed source limit or contain no text; no partial extraction')
    complete = ' '.join(text for entries in groups.values() for _, text in entries).casefold()
    if len(complete.split()) < 100 or 'skills framework' not in complete or 'competencies' not in complete:
        raise ExtractionError('Insufficient ICT framework competency text')
    records = []
    for entries in groups.values():
        start, end = entries[0][0], entries[-1][0]
        text = ('PDF text section; page ranges are retrieval boundaries, not competency categories. '
                'Multi-column reading order may differ; consult the original PDF for table relationships. '
                'Image-only pages without text are not transcribed.\n\n')
        text += '\n\n'.join(value for _, value in entries)
        records.append(Evidence(None, run_id, source.id or 0, EvidenceType.EXPLICIT_COMPETENCY.value,
            f'{source.name} — PDF pages {start}–{end}', None, source.organisation,
            f'{page.url}#page={start}', text, datetime.now().astimezone(), 'EXPLICIT'))
    return records
