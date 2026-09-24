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
