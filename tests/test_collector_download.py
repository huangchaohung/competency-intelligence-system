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


def test_completion_flag_cannot_automatically_prepare(monkeypatch):
    from src.dashboard import collector
    def forbidden(*args, **kwargs):
        raise AssertionError('Preparation needs a click')
    monkeypatch.setattr(collector, 'build_transfer_handover', forbidden)
    app = AppTest.from_string('''
from types import SimpleNamespace
from src.dashboard.collector import render_download
render_download(SimpleNamespace(id=1, completed_at=True), [object()], None, prepare_now=True)
''').run()
    assert not app.exception
    assert app.button[0].label == 'Prepare download files'
    assert not app.get('download_button')


def test_preparation_displays_individual_parts_and_caches_them(monkeypatch):
    from src.dashboard import collector
    def build(*args, **kwargs):
        return {f'public_evidence_part_{i:03}.txt': b'{}' for i in range(1, 4)}
    monkeypatch.setattr(collector, 'build_transfer_handover', build)
    app = AppTest.from_string('''
from types import SimpleNamespace
from src.dashboard.collector import render_download
render_download(SimpleNamespace(id=77, completed_at=True), [object()], None)
''').run()
    assert not app.get('download_button')
    app.button[0].click().run()
    assert not app.exception
    buttons = app.get('download_button')
    assert [b.proto.label for b in buttons[:3]] == ['Download part 1 of 3', 'Download part 2 of 3', 'Download part 3 of 3']
    assert all(b.proto.ignore_rerun for b in buttons[:3])
    assert '3 compact TXT' in app.success[0].value
    app.run()
    assert len(app.get('download_button')) == 4  # parts plus diagnostic download
