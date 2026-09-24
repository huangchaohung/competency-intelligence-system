from streamlit.testing.v1 import AppTest


def test_cloud_alias_uses_canonical_main():
    import app
    import cloud_app
    assert cloud_app.main is app.main


def test_canonical_app_is_read_only_without_admin_secret(monkeypatch, tmp_path):
    import app
    closed = []
    class Connection:
        def close(self):
            closed.append(True)
    monkeypatch.setattr(app, 'ROOT', tmp_path)
    monkeypatch.setattr(app, 'initialise_cloud_root', lambda root: root)
    monkeypatch.setattr(app, 'build_services', lambda root: {'connection': Connection()})
    monkeypatch.setattr(app.collector, 'home', lambda services: None)
    test = AppTest.from_string('import app\napp.main()').run()
    assert not test.exception
    assert test.sidebar.radio[0].options == ['Home', 'Scan & Download']
    assert any('Read-only mode' in item.value for item in test.info)
    assert closed == [True]
