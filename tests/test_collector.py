from types import SimpleNamespace
from src.dashboard.collector import manual_health_rows


def test_health_advice_is_manual_only():
    run = SimpleNamespace(error_summary=None, sources_snapshot=({'id': 1, 'name': 'Example', 'url': 'https://example.org', 'llm_allowed': True},))
    rows = manual_health_rows(run, [])
    assert rows[0]['Status'] == 'No evidence'
    assert 'LLM fallback allowed' not in rows[0]
    assert 'official course' in rows[0]['Suggested action']


def test_collector_services_do_not_load_ai(tmp_path, monkeypatch):
    import builtins
    import app
    from pathlib import Path
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    (tmp_path / 'config').mkdir()
    (tmp_path / 'data').mkdir()
    (tmp_path / 'config' / 'sources.yaml').write_text('sources: []\n', encoding='utf-8')
    original = builtins.__import__
    def guarded(name, *args, **kwargs):
        assert not name.startswith(('openai', 'src.llm')), name
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', guarded)
    services = app.build_services(tmp_path)
    try:
        assert not any('recommendation' in key or 'framework' in key or 'fallback' in key for key in services)
        assert services['source_repository'].list_enabled() == []
    finally:
        services['connection'].close()
