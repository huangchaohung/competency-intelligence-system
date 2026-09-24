from streamlit.testing.v1 import AppTest


def test_cloud_alias_uses_canonical_main():
    import app
    import cloud_app
    assert cloud_app.main is app.main


def test_canonical_app_has_no_admin_and_session_navigation(monkeypatch, tmp_path):
    import app
    closed = []
    class Connection:
        def close(self):
            closed.append(True)
    monkeypatch.setattr(app, 'ROOT', tmp_path)
    monkeypatch.setattr(app, 'refresh_scan_runtime', lambda services: False)
    from threading import Lock
    monkeypatch.setattr(app, 'build_session_services', lambda root: {'connection': Connection(), 'lock': Lock()})
    monkeypatch.setattr(app.collector, 'home', lambda services: None)
    test = AppTest.from_string('import app\napp.main()').run()
    assert not test.exception
    assert test.sidebar.radio[0].options == ['Home', 'Source Configuration', 'Scan & Download']
    assert not test.text_input
    assert closed == []
    test.sidebar.button[0].click().run()
    assert not test.exception
    assert closed == [True]


def test_active_scan_shows_progress_instead_of_lock_message(monkeypatch, tmp_path):
    import app
    from threading import Lock
    class Job:
        def snapshot(self):
            return dict(running=True, completed=40, total=255, source='Example University', stage='start', error=None)
    lock = Lock()
    lock.acquire()
    monkeypatch.setattr(app, 'ROOT', tmp_path)
    monkeypatch.setattr(app, 'build_session_services', lambda root: {'lock': lock, 'scan_job': Job()})
    test = AppTest.from_string('import app\napp.main()').run()
    assert not test.exception
    progress = test.get('progress')[0].proto
    assert '40/255' in progress.text
    assert any('Example University' in item.value for item in test.markdown)
    assert not any('current operation is still running' in item.value for item in test.info)
    lock.release()
