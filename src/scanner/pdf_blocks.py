"""Conservative paragraph recovery; never infer PDF table relationships."""
import re


class PdfBlocks(list):
    """Retain format provenance even for PDF downloads without a .pdf URL."""


def usable_pdf_unit(text):
    """Reject obvious broken endings and tiny fragments; never complete missing text.

    Short named module codes remain useful. This guard is not a semantic validator.
    """
    if re.search(r'[-–—]\s*$', text):
        return False
    return len(text.split()) >= 6 or bool(re.search(r'\b[A-Z]{2,}[- ]?\d{3,}\b', text))


def pdf_blocks(pages):
    """Join likely wrapped prose within a page, keeping lists and layout boundaries.

    Only lowercase continuations are joined. Ambiguous column/table rows remain
    separate; this is not OCR or a reconstruction of a document's reading order.
    """
    blocks = PdfBlocks()
    for page in pages:
        pending = ''
        for raw in page.splitlines():
            line = re.sub(r'\s+', ' ', raw).strip()
            boundary = (not line or bool(re.fullmatch(r'(?:Page )?\d+(?: of \d+)?', line, re.I))
                        or bool(re.search(r'\S[ \t]{3,}\S', raw)))
            if boundary:
                if pending:
                    blocks.append(pending)
                    pending = ''
                if line and not re.fullmatch(r'(?:Page )?\d+(?: of \d+)?', line, re.I):
                    blocks.append(line)
                continue
            continuation = (pending and line[0].islower()
                            and not re.search(r'[.!?:;\-–—]$', pending)
                            and len(pending.split()) >= 5)
            if continuation:
                pending += ' ' + line
            else:
                if pending:
                    blocks.append(pending)
                pending = line
        if pending:
            blocks.append(pending)
    return blocks
