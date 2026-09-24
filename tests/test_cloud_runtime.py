from src.services.cloud_runtime import authorised, password_token, initialise_cloud_root


def test_admin_fails_closed():
    password = 'a-long-test-password-123456'
    assert not authorised('', '')
    assert not authorised('short', password_token('short'))
    assert not authorised(password, password_token('wrong'))
    assert authorised(password, password_token(password))
    assert not authorised(password + 'rotated', password_token(password))


def test_cloud_seed_is_separate_and_preserves_edits(tmp_path):
    (tmp_path / 'config').mkdir()
    (tmp_path / 'config/sources.yaml').write_text('sources: []')
    (tmp_path / 'data').mkdir()
    (tmp_path / 'data/private.db').write_text('private')
    root = initialise_cloud_root(tmp_path)
    assert not (root / 'data').exists()
    target = root / 'config/sources.yaml'
    target.write_text('edited')
    initialise_cloud_root(tmp_path)
    assert target.read_text() == 'edited'


def test_cloud_lock_released_after_exception(tmp_path):
    from filelock import FileLock, Timeout
    import pytest
    path = str(tmp_path / 'app.lock')
    with pytest.raises(ValueError):
        with FileLock(path, timeout=0):
            with pytest.raises(Timeout):
                with FileLock(path, timeout=0):
                    pass
            raise ValueError('test')
    with FileLock(path, timeout=0):
        pass


def test_deployment_allowlist_excludes_data():
    from pathlib import Path
    from scripts.package_cloud import deployment_files
    root = Path(__file__).resolve().parents[1]
    paths = [p.relative_to(root).as_posix() for p in deployment_files(root)]
    assert 'cloud_app.py' in paths
    assert 'config/sources.yaml' in paths
    assert all(not p.startswith(('data/', 'logs/', '.env', '.streamlit/')) for p in paths)
