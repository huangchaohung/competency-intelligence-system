"""Export fixed diagnostic categories, never raw exception text or secrets."""
import re


def source_diagnostics(run):
    names = [str(s.get('name', '')) for s in run.sources_snapshot if s.get('name')]
    if not names or not run.error_summary:
        return {}
    # Workflow separates source errors with '; '. Match full snapshot names,
    # not substrings (e.g. ICE versus ICE Attributes).
    pattern = re.compile(r'(?:^|; )(' + '|'.join(re.escape(n) for n in sorted(set(names), key=len, reverse=True)) + r'): ')
    matches = list(pattern.finditer(run.error_summary))
    result = {}
    rules = {
        'ROBOTS_RESTRICTED': ('robots.txt', 'not permitted'),
        'ACCESS_BLOCKED': ('incapsula', 'access-blocked', '403 client error', '401 client error', 'http 403', 'http 401'),
        'TIMEOUT': ('timeout', 'timed out'),
        'NETWORK_ERROR': ('connection aborted', 'remotedisconnected', 'connection reset', 'name resolution', 'sslerror'),
        'HTTP_ERROR': ('404 client error', '429 client error', '500 server error', '502 server error', '503 server error', '504 server error'),
        'UNEXPECTED_REDIRECT': ('redirected away',),
        'LISTING_MISSING': ('course listing unavailable',),
        'BROWSER_ERROR': ('browser retrieval failed', 'browser has been closed', 'executable doesn\'t exist', 'browser launch failed'),
        'PDF_INVALID_RESPONSE': ('expected pdf but received', 'not the reviewed pdf'),
        'PDF_EXTRACTION_ERROR': ('unable to extract pdf', 'no extractable text found'),
        'PDF_RESOURCE_LIMIT': ('pdf exceeds page limit', 'pdf exceeds extracted text limit', 'sections exceed source limit'),
        'DEPENDENCY_ERROR': ('modulenotfounderror', 'importerror', 'cannot import name', 'no module named', 'requires pypdf'),
        'CODE_ERROR': ('nameerror:', 'typeerror:', 'attributeerror:', 'unboundlocalerror:'),
        'EMPTY_HTML': ('no readable html',),
        'CONTENT_BODY_MISSING': ('body unavailable', 'body missing', 'content block unavailable', 'curriculum unavailable'),
        'INSUFFICIENT_TEXT': ('insufficient', 'title but no substantive'),
        'NO_LINKS': ('no permitted',),
        'RESPONSE_TOO_LARGE': ('exceeds size limit',),
        'UNSUPPORTED_CONTENT': ('did not return html',),
    }
    for i, match in enumerate(matches):
        text = run.error_summary[match.end():matches[i+1].start() if i+1 < len(matches) else None].casefold()
        codes = [code for code, markers in rules.items() if any(m in text for m in markers)] or ['OTHER_SCAN_ERROR']
        existing = result.setdefault(match.group(1), [])
        existing.extend(code for code in codes if code not in existing)
    return result
