"""Canonical entrypoint for local and cloud use, with shared-trial safeguards."""
from pathlib import Path
import streamlit as st
from filelock import FileLock, Timeout
from src.services.collector_services import build_services
from src.dashboard import collector, source_configuration
from src.services.cloud_runtime import authorised, password_token, initialise_cloud_root

ROOT = Path(__file__).resolve().parent


def main():
    st.set_page_config(page_title='STE Collector — Cloud Trial', layout='wide')
    st.warning('Public information only. Viewers share the latest scan result. Download your TXT archive before leaving; cloud storage is temporary.')
    try:
        password = str(st.secrets.get('ADMIN_PASSWORD', ''))
    except FileNotFoundError:
        password = ''
    admin = authorised(password, st.session_state.get('admin_token', ''))
    with st.sidebar.expander('Administrator access'):
        if admin:
            if st.button('Sign out'):
                st.session_state.pop('admin_token', None)
                st.rerun()
        elif len(password) >= 20:
            with st.form('admin_login', clear_on_submit=True):
                entered = st.text_input('Administrator password', type='password')
                submit = st.form_submit_button('Sign in')
            if submit:
                if authorised(password, password_token(entered)):
                    st.session_state['admin_token'] = password_token(entered)
                    st.rerun()
                else:
                    st.error('Incorrect password.')
        else:
            st.info('Read-only mode. Administrator password is not configured (minimum 20 characters).')
    pages = {'Home': collector.home, 'Scan & Download': lambda services: collector.run_scan(services, allow_scan=False)}
    if admin:
        pages = {'Home': collector.home, 'Source Configuration': source_configuration.render,
                 'Scan & Download': collector.run_scan}
    selected = st.sidebar.radio('Navigation', list(pages))
    # Serialize ALL app DB/config access, including startup synchronization.
    # Nonblocking: other sessions get a message rather than starting another scan.
    runtime = ROOT / '.cloud_runtime'
    runtime.mkdir(exist_ok=True)
    try:
        with FileLock(str(runtime / 'app.lock'), timeout=0):
            root = initialise_cloud_root(ROOT)
            services = build_services(root)
            try:
                pages[selected](services)
            finally:
                services['connection'].close()
    except Timeout:
        st.info('Another session is scanning or updating the app. Please return when it finishes.')


if __name__ == '__main__':
    main()
