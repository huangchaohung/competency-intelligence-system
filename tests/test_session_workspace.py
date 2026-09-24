from dataclasses import replace
from datetime import datetime
import pytest
from src.core.exceptions import ConfigurationError
from src.models.domain import Evidence
from src.services.session_workspace import build_session_services, clear_current_scan, parse_source_csv, session_sources_csv


def root_with_master(tmp_path):
    (tmp_path / 'config').mkdir()
    master = tmp_path / 'config/sources.yaml'
    master.write_text('sources:\n  - name: Default\n    organisation: Test\n    url: https://example.org/course\n', encoding='utf-8')
    return master


def test_sessions_and_master_are_isolated(tmp_path):
    master = root_with_master(tmp_path)
    before = master.read_bytes()
    first, second = build_session_services(tmp_path), build_session_services(tmp_path)
    try:
        source = first['source_repository'].list_all()[0]
        first['source_configuration_workflow'].replace_catalogue([replace(source, name='My edit')])
        run = first['scan_repository'].create_run(datetime.now().astimezone(), [])
        first['scan_repository'].add_evidence(Evidence(None, run.id, source.id, 'Article', 'Private to session', None, 'Test', 'https://example.org/course', 'Substantive content', datetime.now().astimezone(), 'EXPLICIT'))
        assert run.id
        assert first['scan_repository'].count_evidence() == 1
        assert second['scan_repository'].count_evidence() == 0
        assert not second['scan_repository'].list_runs()
        assert second['source_repository'].list_all()[0].name == 'Default'
        assert master.read_bytes() == before
        assert set(tmp_path.iterdir()) == {tmp_path / 'config'}
        assert first['connection'].execute('PRAGMA database_list').fetchone()[2] == ''
        clear_current_scan(first)
        assert first['scan_repository'].count_evidence() == 0
        assert not first['scan_repository'].list_runs()
        assert first['source_repository'].list_all()[0].name == 'My edit'
    finally:
        first['connection'].close()
        second['connection'].close()
    fresh = build_session_services(tmp_path)
    assert not fresh['scan_repository'].list_runs()
    assert fresh['source_repository'].list_all()[0].name == 'Default'
    fresh['connection'].close()


def test_csv_roundtrip_and_validation(tmp_path):
    root_with_master(tmp_path)
    services = build_session_services(tmp_path)
    try:
        sources = services['source_repository'].list_all()
        parsed = parse_source_csv(session_sources_csv(sources).encode(), services['configuration_service'])
        assert parsed[0].url == sources[0].url
        assert parsed[0].enabled == sources[0].enabled
        with pytest.raises(ConfigurationError):
            parse_source_csv(b'Name,Organisation,Discovery URL\nBad,Test,http://example.org', services['configuration_service'])
        assert services['source_repository'].list_all() == sources
        with pytest.raises(ConfigurationError):
            parse_source_csv(b'Name,Organisation,Discovery URL\nIncomplete,', services['configuration_service'])
    finally:
        services['connection'].close()
