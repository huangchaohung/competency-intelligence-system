"""Session-only public collector. The master source catalogue is read-only."""
from pathlib import Path
import streamlit as st
from src.dashboard import collector, source_configuration
from src.services.session_workspace import build_session_services, refresh_scan_runtime, RUNTIME_REVISION
from src.services.scan_job import ScanJob
# Kept for legacy integration callers, never used by this entrypoint.
from src.services.collector_services import build_services

ROOT = Path(__file__).resolve().parent


def main():
    st.set_page_config(page_title='STE Public Evidence Collector', layout='wide')
    st.caption('Your temporary workspace · Public information only · Download before leaving')
    st.caption(f'App build: {RUNTIME_REVISION}')
    if 'workspace' not in st.session_state:
        st.session_state['workspace'] = build_session_services(ROOT)
    services = st.session_state['workspace']
    if 'scan_job' not in services:
        services['scan_job'] = ScanJob()
    if services['scan_job'].snapshot()['running']:
        collector.render_scan_progress(services)
        return
    if not services['lock'].acquire(blocking=False):
        collector.render_scan_progress(services)
        return
    try:
        refresh_scan_runtime(services)
        with st.sidebar:
            st.caption('Sources and scan results belong only to this session. The master list is never changed.')
            if st.button('Start fresh', help='Discard this session’s edits and evidence and reload default sources.'):
                services['connection'].close()
                st.session_state.clear()
                st.rerun()
        pages = {'Home': collector.home, 'Source Configuration': source_configuration.render,
                 'Scan & Download': collector.run_scan}
        pages[st.sidebar.radio('Navigation', list(pages))](services)
    finally:
        services['lock'].release()


if __name__ == '__main__':
    main()
