"""CSV-only, bounded competency collection. No catalogue, database or LLM access."""
from __future__ import annotations

import csv
import io
import json
import re
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

PILOT = ('A*STAR', 'BCA', 'CAAS', 'CSA', 'IMDA', 'NASA', 'SSG', 'Michigan', 'DSTA', 'GovTech')
AGENT = 'CompetencyEvidencePilot/1.0'
KEY = re.compile(r'competenc|framework|skills|standards?|certificat|accredit|curricul|programmes?|programs?|courses?|modules?|syllab|learning.outcomes?|training|code.of.practice|licens|handbook', re.I)
BAN = re.compile(r'(^|[/\s_-])(news|technews|media|press|blogs?|magazines?|events?|careers?|internships?|funding|annual.reports?|about)([/\s_-]|$)', re.I)
STRONG = re.compile(r'competenc|framework|standards?|certificat|accredit|curricul|courses?|modules?|syllab|learning.outcomes?|training|handbook|degree|undergraduate|fellowship', re.I)
SUBJECT = re.compile(r'competenc|learning.outcomes?|curricul|syllab|requirements?|modules?|courses?|knowledge|abilities|proficien|assessment|certificat|accredit|standards?|framework|engineering|technical', re.I)
BLOCK = re.compile(r'access denied|verify (?:that )?you are human|checking your browser|captcha|request (?:was )?blocked|enable javascript and cookies', re.I)
MAX_BYTES = 8_000_000


def search_trap(url):
    p = urlsplit(url)
    return bool(re.search(r'/(?:search|search-results)(?:/|$)', p.path, re.I) or
                re.search(r'(?:^|&)(?:search|q|facet|filter|sort|page)=', p.query, re.I))


def frontier_score(url):
    path = urlsplit(url).path.lower()
    return (6 * bool(re.search(r'competenc|framework|curricul|syllab|learning.outcomes|/modules?/', path)) +
            4 * bool(re.search(r'accredit|certificat|/courses?/|coursebook|\.pdf$', path)) +
            min(3, len([part for part in path.split('/') if part])) -
            20 * search_trap(url))


def js_shell(result, parsed):
    if not result or 'html' not in result[2].lower():
        return False
    html = result[1].decode('utf-8', 'replace')
    visible = sum(map(len, parsed[2])) if parsed else len(BeautifulSoup(html, 'html.parser').get_text(strip=True))
    return visible < 500 and bool(re.search(r'id=["\'](?:root|app|__next)["\']|<app-root', html, re.I))


def serial(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def domains(row):
    return [v.lower().strip().rstrip('.') for v in re.split(r'[;,\s]+', row['Allowed_domains']) if v.strip()]


def permitted(url, allowed):
    try:
        p = urlsplit(url)
        host = (p.hostname or '').lower().rstrip('.')
        return (p.scheme in ('http', 'https') and not p.username and not p.password
                and p.port in (None, 80, 443) and any(host == d or host.endswith('.' + d) for d in allowed))
    except ValueError:
        return False


def canonical(url):
    p = urlsplit(url)
    netloc = p.netloc.lower()
    if (p.scheme == 'https' and netloc.endswith(':443')) or (p.scheme == 'http' and netloc.endswith(':80')):
        netloc = netloc.rsplit(':', 1)[0]
    return urlunsplit((p.scheme, netloc, p.path or '/', p.query, ''))


def excluded_resource(url, title, text=''):
    """Conservative exclusions for named non-resource document genres."""
    path = urlsplit(url).path.lower()
    if re.search(r'\bterms and conditions for (?:dcc |project )?support\b|\bcall for projects\b|\bapplication for (?:project |research )?support\b', title, re.I):
        return 'Project support terms/call/application, not competency requirements'
    if re.search(r'/(?:annual-reports?)(?:/|$)', path):
        return 'Annual report, not a competency resource'
    if re.search(r'/submissions-archive/|/government-policy-and-submissions/|dcc.*project.*call|application%20form.*dcc|gls-disqualification', path):
        return 'Policy consultation/support application or land-sales administration, not competency evidence'
    if re.search(r'certification of products and articles|letter of acceptance of type certificate|technical standard order certificate of approval|land sales disqualification|application for support|certificate request|assessment fees and additional services', title, re.I):
        return 'Product approval or administrative transaction, not personnel competency evidence'
    if re.search(r'/(?:members-only|login|signin|sign-in|shibboleth|saml2?|idp|authn|request-information|enquiry|enquire)(?:/|$)', path) or re.search(
            r'^(?:request information|enquir(?:y|e)|sign in|log in)\b', title, re.I):
        return 'Restricted/login/enquiry page, not a public competency resource'
    if re.search(r'/academic-polic(?:ies|es)/|/auditing-courses/?$|/volunteer-for-research-study/|/scholarships/', path):
        return 'Course administration, participant recruitment or scholarship, not competency content'
    if re.search(r'/graduate/education/curriculum-instruction-|/desarrollo-de-competencias-gerenciales-', path):
        return 'Non-STE education or generic management programme'
    if re.search(r'/how-much-does-it-cost/|/how-to-apply/admission-to-', path):
        return 'Fees or application admission instructions, not competency curriculum'
    if re.fullmatch(r'/handbooks/(?:home\.html)?', path) and re.search(r'\d{4} Handbooks', title, re.I):
        return 'Generic handbook index without specific curriculum or learning outcomes'
    if re.search(r'/(?:asbmb-today|asbmbtoday|consultations?|press-releases?)(?:/|$)', path):
        return 'News/magazine/consultation page, not a competency resource'
    if re.search(r'\b(?:comments to|consultation|proposed reforms|task force report|extracurriculars|meet the .*delegates)\b', title, re.I):
        return 'Commentary, consultation, biography or general student-life content'
    if re.search(r'vehicle parking certificate|standards and regulation board|\btemplate\b|pre-standardization activities', title, re.I):
        return 'Administrative permit/governance/template, not substantive competency requirements'
    if re.search(r'\bIET comments to\b|\bresponse to (?:the )?consultation\b', text[:1500], re.I):
        return 'Consultation response, not a standard or competency framework'
    return ''


def browser_policy(row):
    value = row['Browser_rendering'].strip().lower()
    required = value == 'required'
    enabled = required or value in ('yes', 'try plain fetch, then browser rendering') or row['Mode'] == 'RETEST'
    return enabled or 'browser rendering' in row['Notes'].lower(), required


def load_rows(path, rescan=False):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    seen, caps = set(), {}
    required = ('Scan_ID', 'Mode', 'Parent_organisation', 'Organisation_as_listed', 'Source_type',
                'URL', 'Allowed_domains', 'Max_cards', 'Max_chars_per_card', 'Max_chars_per_organisation',
                'Notes', 'Browser_rendering', 'Page_types_to_find')
    for row in rows:
        if rescan:
            row.setdefault('Mode', 'SCAN')
            row.setdefault('Organisation_as_listed', row.get('Parent_organisation', ''))
            row.setdefault('Source_type', 'UNKNOWN_UNTIL_FETCHED')
        if any(k not in row for k in required):
            raise ValueError('CSV missing required columns')
        if not re.fullmatch(r'[NU]\d+' if rescan else r'N\d+', row['Scan_ID']) or row['Scan_ID'] in seen:
            raise ValueError('Invalid or repeated Scan_ID')
        seen.add(row['Scan_ID'])
        if row['Mode'] not in ('SCAN', 'RETEST', 'DISCOVER'):
            raise ValueError('Invalid Mode')
        for field in ('Max_cards', 'Max_chars_per_card', 'Max_chars_per_organisation'):
            row[field] = int(row[field])
            if row[field] <= 0:
                raise ValueError('Limits must be positive')
        if not domains(row) or not permitted(row['URL'], domains(row)):
            raise ValueError('Seed outside Allowed_domains: ' + row['Scan_ID'])
        parent, cap = row['Parent_organisation'], row['Max_chars_per_organisation']
        if not parent or caps.setdefault(parent, cap) != cap:
            raise ValueError('Inconsistent organisation budget')
    return sorted(rows, key=lambda r: (r['Source_type'] == 'RESEARCH', int(r['Scan_ID'][1:])))


def extract(data, content_type, url):
    """Return title, headings, substantive blocks and candidate links; never navigation."""
    if data.startswith(b'%PDF-'):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        if len(reader.pages) > 300:
            raise ValueError('PDF exceeds 300-page extraction bound')
        from src.scanner.pdf_blocks import pdf_blocks
        lines = pdf_blocks(p.extract_text() or '' for p in reader.pages)
        title = str((reader.metadata or {}).get('/Title') or '')
        if not title or title.lower().endswith(('.doc', '.docx')):
            title = ' '.join(lines[:3])[:160]
        return title, ' '.join(lines[:15]), lines, []
    if 'pdf' in content_type or urlsplit(url).path.lower().endswith('.pdf'):
        raise ValueError('Expected PDF; received non-PDF response')
    soup = BeautifulSoup(data, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'svg']):
        tag.decompose()
    links = [(canonical(urljoin(url, a['href'])), a.get_text(' ', strip=True)) for a in soup.select('a[href]')]
    title = soup.title.get_text(' ', strip=True) if soup.title else ''
    # CSS comma selectors return document order: a government masthead may be an
    # <article> before the real <main>. Prefer semantic main explicitly.
    body = soup.select_one('main') or soup.select_one('[role=main]') or soup.select_one('article') or soup.body or soup
    for tag in body.select('nav, header, footer, aside, form, [role=navigation], [class*=cookie], [id*=cookie]'):
        tag.decompose()
    main_links = [(canonical(urljoin(url, a['href'])), a.get_text(' ', strip=True)) for a in body.select('a[href]')]
    links = list(dict.fromkeys(main_links + links))
    headings = ' '.join(t.get_text(' ', strip=True) for t in body.select('h1, h2, h3'))
    if not title and body.h1:
        title = body.h1.get_text(' ', strip=True)
    block_tags = ['h1','h2','h3','h4','h5','h6','p','li','td','dt','dd']
    def own_text(tag):
        return re.sub(r'\s+', ' ', ' '.join(
            str(node).strip() for node in tag.find_all(string=True)
            if node.find_parent(block_tags) is tag)).strip()
    blocks = []
    outcome_section = False
    section_heading = ''
    for tag in body.select('h1,h2,h3,h4,h5,h6,p,li,td,dt,dd'):
        # Parent cells/list items may contain the same paragraphs/list items.
        # Read their own text only; descendants are processed in document order.
        text = own_text(tag)
        list_context = ''
        for parent in tag.find_parents('li'):
            label = own_text(parent)
            # Editors commonly wrap the parent label in a paragraph. Read only
            # immediate paragraphs before the nested list, never its descendants.
            if not label:
                labels = []
                for child in parent.children:
                    if getattr(child, 'name', None) in ('ul', 'ol'):
                        break
                    if getattr(child, 'name', None) == 'p':
                        labels.append(own_text(child))
                label = ' '.join(labels)
            if re.match(r'^(?:skills and competencies|competencies|learning outcomes|required modules|core modules|course content)\b', label, re.I):
                list_context = label.split(':', 1)[0]
                break
        if tag.name.startswith('h') or tag.name == 'dt':
            outcome_section = bool(re.search(r'learning outcomes|what you.ll learn|intended learning|competenc(?:ies|y requirements)|course content', text, re.I))
            section_heading = text
        # Preserve heading context for short action statements without inventing source claims.
        if list_context and text:
            if not text.casefold().startswith((list_context + ':').casefold()):
                text = list_context + ': ' + text
        elif outcome_section and tag.name not in ('h1','h2','h3','h4','h5','h6','dt') and text:
            text = section_heading + ': ' + text
        elif section_heading and re.search(r'prerequisit|prior knowledge|reading|bibliograph|assessment method|teaching method', section_heading, re.I) and text and tag.name not in ('h1','h2','h3','h4','h5','h6','dt'):
            text = section_heading + ': ' + text
        blocks.append(text)
    return title, headings, list(dict.fromkeys(b for b in blocks if b)), links


def qualification(url, title, headings, blocks):
    path = urlsplit(url).path
    if search_trap(url):
        return False, 'Search/faceted listing is not a competency resource'
    if re.search(r'aircraft type.certification|cybersecurity labelling|amusement.ride', title + ' ' + headings, re.I) and not re.search(
            r'personnel|professional competenc|learning outcomes|training course|qualified (?:engineer|person)', ' '.join(blocks), re.I):
        return False, 'Product/asset certification without explicit personnel competency or training requirements'
    excluded = excluded_resource(url, title, ' '.join(blocks))
    if excluded:
        return False, excluded
    if BLOCK.search(' '.join(blocks)[:8000]) and sum(map(len, blocks)) < 15000:
        return False, 'Access/challenge notice; not evidence'
    # Publication directories are excluded; an actual framework under /publications/ is allowed.
    cebok = (urlsplit(url).hostname or '').lower() in ('asce.org', 'www.asce.org') and bool(re.match(r'^/career-growth/cebok(?:/|$)', path))
    # /media/ is also a binary document store. Exempt that segment only for
    # PDF URLs; the document title/body must still pass all resource checks.
    tested_path = re.sub(r'/media/', '/documents/', path, flags=re.I) if path.lower().endswith('.pdf') else path
    if (BAN.search(tested_path) or BAN.search(title.split('|')[0])) and not cebok:
        return False, 'Excluded news/about/events/careers/funding content'
    if re.search(r'publication (?:list|library)|annual report', title + ' ' + headings, re.I):
        return False, 'Publication listing/annual report'
    resource_heading = title + ' ' + headings
    body_signal = bool(re.search(r'learning outcomes|on completion of (?:this|the) course|assessment criteria|competency levels|module (?:code|list)|what you.ll learn', ' '.join(blocks), re.I))
    if not KEY.search(resource_heading) and not re.search(r'body of knowledge|learning outcomes|unit of study', resource_heading, re.I) and not cebok and not body_signal:
        return False, 'No competency/course/standard heading'
    if not STRONG.search(title) and not re.search(r'competenc|framework|standards?|certificat|accredit|curricul|courses?|modules?|syllab|learning.outcomes?|body of knowledge|unit of study', headings, re.I) and not cebok and not body_signal:
        return False, 'Generic programme/project page, not an identified competency resource'
    if re.search(r'fellowship|undergraduate|programme|program\b', title, re.I) and not re.search(
            r'curricul|learning outcomes|credits|modules|will learn|training in|trained in|biodesign process|needs (?:identification|finding)', ' '.join(blocks), re.I):
        return False, 'Programme promotion without curriculum, modules or learning outcomes'
    if re.search(r'customi[sz]ed training|courses by format', title, re.I) and not re.search(
            r'module code|required modules|participants will (?:be able to|learn|apply)|on completion.*(?:able to|apply|design)', ' '.join(blocks), re.I):
        return False, 'Training promotion without explicit curriculum or learner capabilities'
    if not any(SUBJECT.search(b) and len(b) >= 50 for b in blocks):
        return False, 'No substantive competency-bearing text'
    return True, ''


def make_card(row, url, title, blocks, remaining):
    # Pick headed, exact evidence fragments, not a generated summary or navigation sample.
    useful = [b for b in blocks if ((SUBJECT.search(b) and len(b) >= 50) or re.search(r'\b[A-Z]{2,}\s?\d{3,}\b', b) or
              re.search(r'^(?:skills and competencies|competencies|required modules|core modules|learning outcomes|what you.ll learn|intended learning|course content):\s+\S', b, re.I))
              and not re.search(r'^(?:[“\"]|I |My |We are|Assistant Professor|Professor,)|\bI (?:gained|learned|am|was|had)|testimoni|funding|networking|licence application process', b, re.I)]
    # Requirements, outcomes and named module codes outrank promotional introductions.
    useful.sort(key=lambda b: -sum(bool(re.search(p, b, re.I)) for p in
                                 (r'learning outcomes|curriculum|competencies|proficiencies',
                                  r'\b[A-Z]{2,}\s?\d{3,}\b|credits|modules|must|shall',
                                  r'risk management|systems engineering|requirements|skills include')))
    useful.sort(key=lambda b: (
        -int(bool(re.search(r'^(?:skills and competencies|required modules|core modules|learning outcomes|what you.ll learn|intended learning|competenc(?:ies|y requirements)|course content)\b', b, re.I))),
        int(bool(re.search(r'prerequisit|prior knowledge|reading|bibliograph|recommended text|textbook|text book|moodle|lecture slides|course fees|register now', b, re.I)))))
    text = '\n'.join(useful)
    if not text:
        return None
    source_type = row['Source_type']
    if source_type == 'UNKNOWN_UNTIL_FETCHED':
        source_type = 'FRAMEWORK' if re.search(r'framework|competenc|standards?|handbook|\bCEBOK\b|body of knowledge', title, re.I) else 'CATALOGUE'
    card = dict(id=row['Scan_ID'] + '-' + str(row.get('_card_number', 1)),
                parent_organisation=row['Parent_organisation'], organisation=row['Organisation_as_listed'],
                scan_id=row['Scan_ID'], mode=row['Mode'], source_type=source_type,
                title=title[:160], url=url, article_text='', text_shortened=True)
    if row.get('Export_id'):
        card.update(export_id=row['Export_id'], schema_version='ste-competency-cards/2.0',
                    publication_date=None, country='Unknown',
                    evidence_type='Framework or standard' if source_type == 'FRAMEWORK' else 'Course or curriculum',
                    priority=1 if source_type == 'FRAMEWORK' else 2,
                    original_text_characters=len('\n'.join(blocks)),
                    excerpt_method='Selected complete blocks or sentences; not a full inventory')
    if row.get('Source_family'):
        card.update(source_family=row['Source_family'], publisher_host=urlsplit(url).hostname,
                    retrieval_method='CRAWLER')
    if 'Verification' in row:
        card.update(retrieval_method='CRAWLER', publisher_host=urlsplit(url).hostname,
                    seed_verification_reported=row['Verification'])
    budget = min(row['Max_chars_per_card'], remaining)
    # Include serialization escaping in all budgets; omit rather than emit unusable tiny text.
    # Fit whole original blocks/sentences, never an arbitrary prefix.
    units = [unit.strip() for block in useful
             for unit in re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', block) if unit.strip()]
    selected = []
    seen_units = set()
    for unit in units:
        key = ' '.join(unit.casefold().split())
        if key in seen_units:
            continue
        seen_units.add(key)
        candidate = '\n'.join(selected + [unit])
        card['article_text'] = candidate
        if len(serial(card)) <= budget:
            selected.append(unit)
    excerpt = '\n'.join(selected)
    if not row.get('Export_id'):
        # Historical CLI exports retain their original caller-selected budget contract.
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            card['article_text'] = text[:mid]
            if len(serial(card)) <= budget:
                lo = mid
            else:
                hi = mid - 1
        excerpt = text[:lo]
        if lo < len(text):
            excerpt = excerpt.rsplit(' ', 1)[0]
    if len(excerpt) < 80:
        return None
    card['article_text'] = excerpt
    # Always true: selecting qualifying blocks omits some original document material.
    return card


class PilotCollector:
    def __init__(self):
        self.logs, self.cards, self.statuses = [], [], []
        self.session = requests.Session()
        self.session.headers['User-Agent'] = AGENT
        self.robots, self.seen = {}, set()
        self.content_attempts = set()
        self.sitemap_origins = set()

    def log(self, row, url, status='', rendering='plain', reason='', purpose='content', attempted=False):
        item = dict(Scan_ID=row['Scan_ID'], url=url, http_status=status, rendering_used=rendering,
                    cards_produced=0, chars=0, reason_if_rejected=reason, purpose=purpose, attempted=attempted,
                    parent_organisation=row.get('Parent_organisation', ''), configured_url=row.get('URL', ''),
                    text_sample='', resolved_url='')
        if 'Verification' in row:
            item['seed_verification_reported'] = row['Verification']
        self.logs.append(item)
        return item

    def raw(self, row, url, purpose='content', check_robots=True):
        for _ in range(6):
            url = canonical(url)
            if purpose == 'content':
                identity = (row.get('Scan_ID'), url)
                if identity in self.content_attempts:
                    self.log(row, url, reason='Duplicate resolved content URL in this source; not requested', purpose=purpose)
                    return None
                self.content_attempts.add(identity)
                if excluded_resource(url, '') == 'Annual report, not a competency resource':
                    self.log(row, url, reason='Annual report excluded before download', purpose=purpose)
                    return None
            if excluded_resource(url, '') == 'Restricted/login/enquiry page, not a public competency resource':
                self.log(row, urlsplit(url)._replace(query='', fragment='').geturl(),
                         reason='Restricted/login/enquiry destination; not requested', purpose=purpose)
                return None
            if not permitted(url, domains(row)):
                self.log(row, url, reason='Outside Allowed_domains; not requested', purpose=purpose)
                return None
            if check_robots and not self.allowed_by_robots(row, url):
                self.log(row, url, reason='robots disallows or unavailable; not requested', purpose=purpose)
                return None
            entry = self.log(row, url, purpose=purpose, attempted=True)
            try:
                with self.session.get(url, timeout=(8, 18), allow_redirects=False, stream=True) as response:
                    entry['http_status'] = response.status_code
                    if response.is_redirect:
                        entry['reason_if_rejected'] = 'Redirect'
                        url = canonical(urljoin(url, response.headers['Location']))
                        continue
                    response.raise_for_status()
                    buf = bytearray()
                    started = time.monotonic()
                    for chunk in response.iter_content(65536):
                        buf.extend(chunk)
                        if len(buf) > MAX_BYTES or time.monotonic() - started > 35:
                            raise ValueError('Response exceeds 8MB/35-second download bound')
                    entry['resolved_url'] = url
                    if response.status_code == 202:
                        entry['reason_if_rejected'] = 'HTTP 202: no completed document response; review source access manually'
                        return None
                    if not buf:
                        entry['reason_if_rejected'] = 'Empty response body; no document to extract'
                        return None
                    return url, bytes(buf), response.headers.get('Content-Type', ''), entry
            except (requests.RequestException, ValueError) as error:
                entry['reason_if_rejected'] = type(error).__name__ + ': ' + str(error)[:240]
                return None
        self.log(row, url, reason='Redirect limit reached', purpose=purpose)
        return None

    def allowed_by_robots(self, row, url):
        p = urlsplit(url)
        origin = f'{p.scheme}://{p.netloc}'
        if origin not in self.robots:
            result = self.raw(row, origin + '/robots.txt', 'robots', False)
            parser = RobotFileParser()
            if result:
                robots_text = result[1].decode('utf-8', 'replace')
                if '<html' in robots_text.lower() or BLOCK.search(robots_text):
                    result[3]['reason_if_rejected'] = 'robots.txt returned HTML/access notice; policy unavailable'
                    self.robots[origin] = None
                    return False
                parser.parse(robots_text.splitlines())
            elif self.logs[-1]['http_status'] in (404, 410):
                parser.parse([])
            else:
                self.robots[origin] = None
                return False
            self.robots[origin] = parser
        parser = self.robots[origin]
        return parser is not None and parser.can_fetch(AGENT, url)

    def rendered(self, row, url):
        if not permitted(url, domains(row)) or not self.allowed_by_robots(row, url):
            self.log(row, url, rendering='browser', reason='Browser not started: domain/robots policy')
            return None
        entry = self.log(row, url, rendering='browser')
        try:
            from playwright.sync_api import sync_playwright
            from src.scanner.browser_runtime import launch_chromium
            with sync_playwright() as pw:
                browser = launch_chromium(pw)
                try:
                    context = browser.new_context(user_agent=AGENT, service_workers='block')
                    def route(request_route):
                        req = request_route.request
                        if req.resource_type in ('image', 'font', 'media'):
                            request_route.abort()
                            return
                        if excluded_resource(req.url, '') == 'Restricted/login/enquiry page, not a public competency resource':
                            self.log(row, urlsplit(req.url)._replace(query='', fragment='').geturl(),
                                     rendering='browser', reason='Restricted/login/enquiry destination; not requested',
                                     purpose='browser_resource')
                            request_route.abort()
                            return
                        if (not permitted(req.url, domains(row)) or
                                not self.allowed_by_robots(row, req.url)):
                            self.log(row, req.url, rendering='browser', reason='Browser request blocked by domain/robots policy', purpose='browser_resource')
                            request_route.abort()
                        else:
                            request_route.continue_()
                    context.route('**/*', route)
                    page = context.new_page()
                    page.on('response', lambda response: self.log(row, response.url, response.status, 'browser', purpose='browser_resource', attempted=True))
                    entry['attempted'] = True
                    response = page.goto(url, wait_until='domcontentloaded', timeout=25000)
                    entry['http_status'] = response.status if response else ''
                    if response and response.status == 202:
                        entry['reason_if_rejected'] = 'HTTP 202: browser did not receive a completed document response'
                        return None
                    page.wait_for_timeout(1500)
                    if response and response.status >= 400:
                        raise ValueError('Browser HTTP failure')
                    data = page.content().encode('utf-8')
                    if len(data) > MAX_BYTES:
                        raise ValueError('Rendered HTML exceeds bound')
                    entry['resolved_url'] = page.url
                    return page.url, data, 'text/html', entry
                finally:
                    browser.close()
        except Exception as error:
            entry['reason_if_rejected'] = type(error).__name__ + ': ' + str(error).splitlines()[0][:240]
            return None

    def candidate_links(self, row, links):
        found = []
        hints = set(re.findall(r'framework|training|course|standard|registration|licens|curricul|certificat', row['Page_types_to_find'].lower()))
        for url, label in links:
            if row['Parent_organisation'] == 'Ngee Ann Polytechnic' and (urlsplit(url).hostname or '').endswith('moe.gov.sg'):
                if not re.match(r'^/coursefinder/coursedetail/n\d', urlsplit(url).path):
                    continue
            if permitted(url, domains(row)) and not search_trap(url) and not excluded_resource(url, label) and KEY.search(urlsplit(url).path + ' ' + label) and not BAN.search(urlsplit(url).path):
                if url not in found:
                    found.append(url)
        return sorted(found, key=lambda u: -(sum(h in u.lower() for h in hints) +
                       4 * bool(re.search(r'learning-outcomes|/curriculum|/modules?/|/coursebook/', u, re.I)) +
                       3 * bool(re.search(r'curricul|competenc|syllab|framework|\.pdf(?:$|\?)', u, re.I))))

    def run(self, rows):
        used = Counter()
        for card in self.cards:
            used[card['parent_organisation']] += len(serial(card))
        for row in rows:
            parent = row['Parent_organisation']
            print(f"{row['Scan_ID']} {parent}: {row['Mode']}", flush=True)
            if row['Source_type'] == 'RESEARCH' and used[parent]:
                self.log(row, row['URL'], reason='SKIPPED_RESEARCH: parent already has cards', rendering='not_attempted')
                continue
            if used[parent] >= row['Max_chars_per_organisation']:
                self.log(row, row['URL'], reason='SKIPPED_PARENT_CAP', rendering='not_attempted')
                continue
            queue, visited, produced = [row['URL']], set(), 0
            discover = row['Mode'] == 'DISCOVER'
            if discover or row.get('Host_retry'):
                p = urlsplit(row['URL'])
                alt = (p.hostname[4:] if p.hostname.startswith('www.') else 'www.' + p.hostname)
                alternate = urlunsplit((p.scheme, alt, p.path, p.query, ''))
                if permitted(alternate, domains(row)):
                    queue.append(alternate)
            p = urlsplit(row['URL'])
            origin = f'{p.scheme}://{p.netloc}'
            if origin not in self.sitemap_origins and (discover or row.get('Export_id')):
                self.sitemap_origins.add(origin)
                # Sitemap traversal itself is bounded, independent of 15 content candidates.
                self.allowed_by_robots(row, row['URL'])
                origin = f'{p.scheme}://{p.netloc}'
                parser = self.robots.get(origin)
                maps = list(dict.fromkeys([origin + '/sitemap.xml'] + (parser.site_maps() or [] if parser else [])))
                for sitemap in maps[:3]:
                    result = self.raw(row, sitemap, 'sitemap')
                    if result:
                        xml = BeautifulSoup(result[1], 'xml')
                        locations = [n.get_text(strip=True) for n in xml.select('url > loc')]
                        queue.extend(self.candidate_links(row, [(u, '') for u in locations]))
                        # One nested index layer, maximum two child sitemaps.
                        for node in xml.select('sitemap > loc')[:2]:
                            child = self.raw(row, node.get_text(strip=True), 'sitemap')
                            if child:
                                queue.extend(self.candidate_links(row, [(n.get_text(strip=True), '') for n in BeautifulSoup(child[1], 'xml').select('url > loc')]))
            limit = 15 if discover else row['Max_cards'] + 1
            while queue and len(visited) < limit and produced < row['Max_cards']:
                queue = sorted(set(queue) - visited, key=lambda u: (-frontier_score(u), u))
                # The officer's explicit seed always gets one attempt before inferred candidates.
                seed = canonical(row['URL'])
                if seed not in visited and seed in queue:
                    queue.remove(seed)
                    queue.insert(0, seed)
                if len(queue) > 100:
                    self.log(row, row['URL'], rendering='not_attempted',
                             reason=f'FRONTIER_PRUNED: {len(queue)-100} lower-ranked candidates not queued')
                    queue = queue[:100]
                if not queue:
                    break
                url = canonical(queue.pop(0))
                if url in visited:
                    continue
                visited.add(url)
                result = self.raw(row, url)
                parsed, good = None, False
                if result:
                    try:
                        parsed = extract(result[1], result[2], result[0])
                        good, reason = qualification(result[0], *parsed[:3])
                        result[3]['reason_if_rejected'] = reason
                        if not good:
                            result[3]['text_sample'] = ' '.join(parsed[2])[:200]
                    except Exception as error:
                        result[3]['reason_if_rejected'] = 'Extraction: ' + str(error)[:200]
                needs_browser, required_browser = browser_policy(row)
                if required_browser or (not good and needs_browser and js_shell(result, parsed)):
                    rendered = self.rendered(row, url)
                    if rendered:
                        try:
                            browser_parsed = extract(rendered[1], rendered[2], rendered[0])
                            browser_good, reason = qualification(rendered[0], *browser_parsed[:3])
                            rendered[3]['reason_if_rejected'] = reason
                            if browser_good or parsed is None:
                                result, parsed = rendered, browser_parsed
                                good = browser_good
                            elif not good:
                                # Keep rendered links for discovery even if no card qualifies.
                                parsed = (*parsed[:3], list(dict.fromkeys(parsed[3] + browser_parsed[3])))
                        except Exception as error:
                            rendered[3]['reason_if_rejected'] = 'Extraction: ' + str(error)[:200]
                if parsed:
                    queue.extend(self.candidate_links(row, parsed[3]))
                if not good or not result or not parsed:
                    continue
                identity = (parent, canonical(result[0]))
                if identity in self.seen:
                    result[3]['reason_if_rejected'] = 'Duplicate parent URL'
                    continue
                row['_card_number'] = produced + 1
                card = make_card(row, result[0], parsed[0], parsed[2], row['Max_chars_per_organisation'] - used[parent])
                if not card:
                    result[3]['reason_if_rejected'] = 'SKIPPED_CHAR_CAP: metadata leaves insufficient substantive excerpt'
                    continue
                if any(c['parent_organisation'] == parent and
                       ' '.join(c['article_text'].lower().split()) == ' '.join(card['article_text'].lower().split())
                       for c in self.cards):
                    result[3]['reason_if_rejected'] = 'Duplicate organisation excerpt; not independent corroboration'
                    continue
                self.cards.append(card)
                self.seen.add(identity)
                size = len(serial(card))
                used[parent] += size
                produced += 1
                result[3].update(cards_produced=1, chars=size, reason_if_rejected='', resolved_url=result[0])
            if queue:
                self.log(row, row['URL'], rendering='not_attempted', reason=f'BOUND_REACHED: {len(set(queue) - visited)} queued URLs not requested')
        return self.summarise(rows)

    def summarise(self, rows):
        self.statuses = []
        used = Counter()
        for card in self.cards:
            used[card['parent_organisation']] += len(serial(card))
        for parent in dict.fromkeys(r['Parent_organisation'] for r in rows):
            ids = {r['Scan_ID'] for r in rows if r['Parent_organisation'] == parent}
            logs = [l for l in self.logs if l['Scan_ID'] in ids]
            cards = [c for c in self.cards if c['parent_organisation'] == parent]
            successful = any(isinstance(l['http_status'], int) and 200 <= l['http_status'] < 300 and l['purpose'] == 'content' for l in logs)
            status = 'DROPPED_NO_COMPETENCY_SOURCE' if successful else 'FAILED_FETCH'
            if cards:
                status = ('SCANNED_RESEARCH_ONLY' if all(c['source_type'] == 'RESEARCH' for c in cards) else
                          'SCANNED' if any(c['mode'] == 'SCAN' for c in cards) else
                          'RECOVERED' if any(c['mode'] == 'RETEST' for c in cards) else 'DISCOVERED')
            errors = [l['reason_if_rejected'] for l in logs if l['reason_if_rejected'] and l['reason_if_rejected'] != 'Redirect']
            self.statuses.append(dict(Parent_organisation=parent, Status=status, cards_produced=len(cards),
                                     chars_produced=used[parent], urls_tried=len({l['url'] for l in logs if l['attempted']}),
                                     last_error=errors[-1] if errors else ''))
        return self


def split_cards(cards, limit=300000):
    parts, current = [], []
    for card in cards:
        if len(serial([card])) >= limit:
            raise ValueError('Single card exceeds file bound')
        if len(serial(current + [card])) >= limit:
            parts.append(serial(current))
            current = []
        current.append(card)
    parts.append(serial(current))
    return parts


def write_outputs(result, directory, txt=False):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    parts = split_cards(result.cards)
    for index, part in enumerate(parts, 1):
        name = f'cards_part_{index:03}.txt' if txt else ('cards.json' if len(parts) == 1 else f'cards_part_{index:03}.json')
        (directory / name).write_text(part, encoding='utf-8')
    for name, records in [('organisation_status.csv', result.statuses), ('url_log.csv', result.logs)]:
        if txt:
            name = name.replace('.csv', '.txt')
        with (directory / name).open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]))
            writer.writeheader()
            for record in records:
                writer.writerow({k: ("'" + v if isinstance(v, str) and v.startswith(('=', '+', '-', '@')) else v) for k, v in record.items()})
