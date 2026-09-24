from streamlit.testing.v1 import AppTest


def test_download_survives_rerun_without_regenerating(monkeypatch):
    from src.dashboard import collector
    monkeypatch.setattr(collector, 'build_transfer_handover', collector.build_transfer_handover)
    app = AppTest.from_string('''
from types import SimpleNamespace
import streamlit as st
from src.dashboard import collector
def build(*args, **kwargs):
    st.session_state['builds'] = st.session_state.get('builds', 0) + 1
    return {'public_evidence_batch_7.txt': b'{"evidence": []}'}
collector.build_transfer_handover = build
collector.render_download(SimpleNamespace(id=7, completed_at=True), [object()], None)
''')
    app.run()
    assert not app.exception
    assert 'builds' not in app.session_state
    assert not app.get('download_button')
    app.button[0].click().run()
    assert app.session_state['builds'] == 1
    downloads = app.get('download_button')
    assert len(downloads) == 2
    assert downloads[0].proto.ignore_rerun
    app.run()
    assert app.session_state['builds'] == 1
    assert not app.exception


def test_incomplete_scan_has_no_download():
    app = AppTest.from_string('''
from types import SimpleNamespace
from src.dashboard.collector import render_download
render_download(SimpleNamespace(id=8, completed_at=None), [], None)
''').run()
    assert not app.exception
    assert not app.get('download_button')
