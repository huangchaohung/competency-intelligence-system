"""Collection-only pages without recommendation dashboard dependencies."""
from math import ceil
import streamlit as st
from src.core.exceptions import CompetencyIntelligenceError
from src.services.source_health_service import source_health_rows
from src.services.public_handover import build_transfer_handover
from src.services.session_workspace import clear_current_scan
from src.services.scan_job import ScanJob


@st.fragment(run_every=1)
def render_scan_progress(services):
    state = services['scan_job'].snapshot()
    if not state['running']:
        if services['lock'].locked():
            st.info('Finishing your current update…')
            return
        st.rerun()
    total, done = state['total'], state['completed']
    fraction = min(1.0, done / max(total, 1))
    st.header('Scanning your sources')
    st.progress(fraction, text=f'{done}/{total} sources completed · {fraction:.0%} · {max(0, total-done)} remaining')
    st.write(f"Current source: {state['source'] or 'Starting…'}")
    st.caption('Each configured source has equal weight. Completed includes sources with errors; review source health afterwards. Some sources take longer than others.')
    st.info('Scanning continues while this progress display refreshes. Please keep this tab open. Editing and reset are available when the scan finishes.')


def fmt(value):
    return value.strftime('%Y-%m-%d %H:%M') if value else 'Unknown'


def manual_health_rows(run, evidence):
    rows = []
    for original in source_health_rows(run, evidence):
        row = {k: v for k, v in original.items() if k not in {'LLM fallback allowed', 'Suggested action'}}
        row['Suggested action'] = {
            'Error': 'Check URL and access permissions; replace manually or disable with a reason.',
            'No evidence': 'Inspect the page; try an official course, programme or document URL.',
            'Low evidence': 'Inspect the text: a single complete resource can be useful.',
            'Healthy': 'Sample actual text for relevance, advertisements and access-block messages.',
        }.get(row['Status'], 'Review manually in Source Configuration.')
        rows.append(row)
    return rows


def home(services):
    st.title('STE Public Evidence Collector')
    st.info('Public sources only. Keep internal frameworks and AI analysis on government-approved systems.')
    st.markdown('1. **Configure sources** — select public websites.\n2. **Scan & Download** — collect public evidence without AI.\n3. **Review and download** — inspect the latest scan and save its TXT file directly to your laptop.\n4. **Analyse securely** — use the downloaded evidence with your approved government assistant. Keep internal frameworks off this website.')
    st.metric('Enabled sources', len(services['source_repository'].list_enabled()))
    st.caption('Your source edits and evidence are temporary and private to this session. A new session starts with default sources and no evidence. Download before leaving; use Start fresh to discard this workspace immediately.')


def run_scan(services, *, allow_scan=True):
    st.header('Scan & Download')
    if services.get('session_only'):
        job = services.setdefault('scan_job', ScanJob())
        if job.snapshot()['running']:
            render_scan_progress(services)
            return
        sources = services['source_repository'].list_enabled()
        st.write(f'{len(sources)} enabled sources. This scan makes no AI requests.')
        if st.button('Scan enabled sources', disabled=not sources, type='primary'):
            for key in list(st.session_state):
                if key.startswith(('public_evidence_only_', 'public_handover_', 'org_', 'page_', 'prepare_txt_')):
                    del st.session_state[key]
            job.start(services, len(sources))
            render_scan_progress(services)
            return
        state = job.snapshot()
        if state['error']:
            st.error(f"Scan stopped: {state['error']}. You can try a new scan.")
        elif state['stage'] == 'finished':
            st.success(f"{state['completed']}/{state['total']} sources completed. Review source health, then prepare your TXT.")
        history(services)
        return
    completed_here = None
    sources = services['source_repository'].list_enabled()
    st.write(f'{len(sources)} enabled sources. This scan makes no AI requests.')
    if not allow_scan:
        st.info('Sign in under Administrator access to run a scan. You can download the latest shared result below.')
    if st.button('Scan enabled sources', disabled=not sources or not allow_scan, type='primary'):
        if services.get('session_only'):
            clear_current_scan(services)
            for key in list(st.session_state):
                if key.startswith(('public_evidence_only_', 'public_handover_', 'org_', 'page_', 'prepare_txt_')):
                    del st.session_state[key]
        progress = st.progress(0.0, text='Starting scan…')
        def update(index, total, name, family, source_type, stage):
            done = index if stage in {'done', 'error'} else index - 1
            progress.progress(done / max(total, 1), text=f'{name} · {done}/{total} finished · {total-done} remaining')
        try:
            with st.spinner('Collecting public evidence…'):
                run = services['scan_workflow'].run(progress_callback=update)
            progress.progress(1.0, text='Scan finished')
            st.success('Scan finished. Prepare and download your current evidence below.')
            completed_here = run.id
            if run.error_summary:
                st.warning(run.error_summary)
        except CompetencyIntelligenceError as error:
            st.error(str(error))
    history(services, completed_here=completed_here)


def history(services, *, completed_here=None):
    """Render the latest result only; retained storage is not a history UI."""
    st.subheader('Current scan result')
    repo = services['scan_repository']
    runs = repo.list_runs(limit=1)
    if not runs:
        st.info('No evidence in this session. Use the default sources, adjust your copy or upload a source CSV, then run a scan.')
        return
    run = runs[0]
    st.caption(f'{fmt(run.started_at)} · Your current scan only. Download before starting another scan or leaving.')
    st.caption(f"Status: {run.status.value.replace('_', ' ').title()}")
    evidence = repo.list_evidence_for_run(run.id)
    summary = repo.get_summary(run.id)
    render_download(run, evidence, summary)
    st.metric('Evidence in this scan', len(evidence))
    if summary is not None:
        st.caption(f"Originally collected: {summary['evidence_count']} evidence records. Source health below was saved when the scan completed.")
        st.subheader('Source health at scan completion')
        st.dataframe(summary['health'], hide_index=True, width='stretch')
        st.caption('Review unsuccessful or low-output sources manually in Source Configuration. Counts alone do not establish content quality.')
    elif run.id not in {r.id for r in runs[:5]} and not evidence:
        st.info('Evidence text is no longer retained for this older batch. Its empty retained list does not mean the sources failed.')
    else:
        st.subheader('Source health and manual URL review')
        st.caption('Counts are initial indicators, not proof of useful content. Inspect actual text.')
        st.dataframe(manual_health_rows(run, evidence), hide_index=True, width='stretch')
    if run.error_summary:
        with st.expander('Recorded scan errors'):
            st.text(run.error_summary)
    with st.expander('Configured sources used in this scan'):
        fields = ('name', 'url', 'organisation', 'source_family', 'source_type')
        st.dataframe([{k: s.get(k, 'Unknown') for k in fields} for s in run.sources_snapshot], hide_index=True, width='stretch')
    st.subheader('Current evidence')
    if evidence:
        org = st.selectbox('Organisation', ['All organisations'] + sorted({e.organisation for e in evidence}), key=f'org_{run.id}')
        visible = [e for e in evidence if org == 'All organisations' or e.organisation == org]
        column, _ = st.columns([1, 4])
        page = column.number_input('Evidence page number', min_value=1, max_value=max(1, ceil(len(visible)/10)), value=1, step=1, key=f'page_{run.id}_{org}')
        start = (page - 1) * 10
        st.caption(f'{start+1}–{min(start+10, len(visible))} of {len(visible)} evidence items')
        for item in visible[start:start+10]:
            with st.expander(f'{item.organisation} · {item.title}'):
                st.text(f'{item.evidence_type} · Fetched {fmt(item.extracted_at)}')
                st.text(item.url)
                st.write(' '.join(item.article_text.split()[:100]))


def render_download(run, evidence, summary, *, prepare_now=False):
    st.subheader('Download evidence TXT')
    st.caption('All evidence from your current scan is included, regardless of preview filters. It is held only in session memory; download to keep your own copy.')
    key = f'public_evidence_only_{run.id}'
    # Bound session memory to one prepared batch, including legacy cache keys.
    for old_key in list(st.session_state):
        if (old_key.startswith('public_handover_') or old_key.startswith('public_evidence_only_')) and old_key != key:
            del st.session_state[old_key]
    if not evidence or not run.completed_at:
        st.info('A completed scan with retained evidence is required for download.')
        return
    requested = False
    if key not in st.session_state:
        st.caption('Opening this page never prepares a file. Click below when you are ready.')
        requested = st.button('Prepare evidence TXT', key=f'prepare_txt_{run.id}')
    if key not in st.session_state and requested:
        try:
            with st.spinner('Preparing complete evidence TXT…'):
                st.session_state[key] = build_transfer_handover(run, evidence, retention_eligible=True, scan_summary=summary)
        except ValueError as error:
            st.error(str(error))
    if key in st.session_state:
        files = st.session_state[key]
        for name, data in files.items():
            filename = 'public_evidence.txt'
            st.download_button('Download evidence TXT', data, file_name=filename, mime='text/plain', on_click='ignore')
            st.caption(f'{filename} · {len(data)/1_000_000:.2f} MB · Full text preserved')
        with st.expander('Download troubleshooting'):
            st.download_button('Download small test TXT', b'STE download test: public text only.\n', file_name='download_test.txt', mime='text/plain', on_click='ignore')
            st.write('If neither file downloads, ask IT whether downloads from this app are permitted. If only the large file fails, record its size and browser error. A new session or server restart loses this scan; download before leaving. Do not bypass government security controls.')
