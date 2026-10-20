"""Resolve organisation-level v5 instructions without inventing seed URLs."""
from urllib.parse import urlsplit

ALIASES = {'Berkeley': 'UC Berkeley', 'Engineering Council': 'Engineering Council UK',
           'Singapore Green Plan 2030': 'Singapore Green Plan'}
LEGACY = {'DSO': 'DSO National Laboratories', 'IES': 'Institution of Engineers Singapore',
          'RAEng': 'Royal Academy of Engineering'}


def compile_plan(master, previous, v4, catalogue):
    sources, plan = [], []
    for parent in master:
        org = parent['Parent_organisation']
        mode = parent['Scan_mode']
        if mode not in ('SCAN', 'RETEST', 'DISCOVER', 'DROP_OR_DISCOVER'):
            raise ValueError('Unsupported scan mode')
        proven = [u.strip() for u in parent.get('Proven_URLs', '').split('|') if u.strip()]
        candidates = [(u, 'v5 supplied leaf URL', {}) for u in proven]
        if not candidates:
            candidates = [(r['URL'], 'v4 seed; not guaranteed healthy', r) for r in v4 if r['Parent_organisation'] == org]
        if not candidates:
            candidates = [(r['URL'], 'v2 registry seed', r) for r in previous if r['Parent_organisation'] == ALIASES.get(org, org)]
        if not candidates:
            candidates = [(r['url'], 'existing catalogue seed; competency relevance unverified', r) for r in catalogue if r['organisation'] == LEGACY.get(org, org)]
        if not candidates:
            raise ValueError('No recorded URL for ' + org)
        seen = set()
        for url, origin, old in candidates:
            if url in seen:
                continue
            seen.add(url)
            if urlsplit(url).scheme != 'https':
                raise ValueError('Non-HTTPS seed: ' + url)
            index = len(plan) + 1
            browser = mode == 'RETEST' or old.get('Browser_rendering') == 'Required' or old.get('use_browser_rendering', False)
            kind = old.get('Source_type', old.get('source_type', 'INDEX'))
            if kind not in ('FRAMEWORK', 'CATALOGUE', 'RESEARCH', 'INDEX', 'ARTICLE', 'TREND'):
                kind = 'INDEX'
            sources.append(dict(name=f'{org} — {index:03}', organisation=org, url=url,
                source_family=parent['Source_family'], source_type=kind,
                source_role='PRIMARY_DISCOVERY', enabled=True, llm_allowed=False,
                max_articles_per_scan=4, max_listing_pages=5, use_browser_rendering=browser,
                article_url_pattern=''))
            plan.append(dict(organisation=org, url=url, mode='DISCOVER' if mode == 'DROP_OR_DISCOVER' else mode,
                requested_mode=mode, provenance=origin, source_family=parent['Source_family'],
                allowed_domains=old.get('Allowed_domains') or urlsplit(url).hostname.removeprefix('www.'),
                page_types_to_find='competency framework curriculum modules learning outcomes courses standards',
                browser_required=old.get('Browser_rendering') == 'Required'))
    return {'sources': sources}, plan
