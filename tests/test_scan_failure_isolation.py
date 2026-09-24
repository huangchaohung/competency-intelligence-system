from datetime import datetime
from types import SimpleNamespace
from threading import Event
import json
import sqlite3
import pytest

from src.core.exceptions import ScanError
from src.models.domain import Evidence, ScanStatus
from src.services.session_workspace import build_session_services
from src.services.scan_job import ScanJob
from src.services.public_handover import build_transfer_handover


def setup_services(tmp_path, monkeypatch, browser_error):
    (tmp_path / 'config').mkdir()
    (tmp_path / 'config/sources.yaml').write_text('''sources:
  - name: A discovery failure
    organisation: Test
    url: https://example.org/discovery
  - name: B NUS curriculum
    organisation: NUS
    url: https://cde.nus.edu.sg/arch/programmes/master-of-urban-planning/curriculum
    use_browser_rendering: true
  - name: C healthy
    organisation: Test
    url: https://example.org/course
''', encoding='utf-8')
    services = build_session_services(tmp_path)
    workflow = services['scan_workflow']
    def discover(source):
        if source.name.startswith('A'):
            raise TimeoutError('Discovery timed out')
        if source.name.startswith('B'):
            return [source.url]
        return [source.url + '/empty', source.url + '/good']
    workflow._router = SimpleNamespace(discover=discover)
    def fetch(url, name):
        if url.endswith('/empty'):
            raise ScanError('No readable HTML')
        return SimpleNamespace(url=url)
    workflow._scanner = SimpleNamespace(fetch_url=fetch)
    def extract(page, source, run_id):
        return Evidence(None, run_id, source.id, 'Article', 'Useful course', None,
                        source.organisation, page.url, 'Real course text ' * 100,
                        datetime.now().astimezone(), 'EXPLICIT')
    workflow._extractor = SimpleNamespace(extract=extract)
    from src.scanner import nus_curriculum
    def blocked(*args):
        raise browser_error('NUS curriculum browser response is empty or access-blocked')
    monkeypatch.setattr(nus_curriculum, 'fetch_curriculum', blocked)
    return services


@pytest.mark.parametrize('browser_error', [ScanError, RuntimeError, type('ScanError', (Exception,), {})])
def test_blocked_sources_continue_and_current_evidence_remains_downloadable(tmp_path, monkeypatch, browser_error):
    services = setup_services(tmp_path, monkeypatch, browser_error)
    try:
        progress = []
        result = services['scan_workflow'].run(lambda *args: progress.append(args))
        assert result.status == ScanStatus.COMPLETED_WITH_ERRORS
        assert 'Discovery timed out' in result.error_summary
        assert 'NUS curriculum browser response is empty or access-blocked' in result.error_summary
        assert 'No readable HTML' in result.error_summary
        assert {row[0] for row in progress if row[-1] in {'done', 'error'}} == {1, 2, 3}
        evidence = services['scan_repository'].list_evidence_for_run(result.id)
        assert len(evidence) == 1
        assert evidence[0].url.endswith('/good')
        summary = services['scan_repository'].get_summary(result.id)
        payload = json.loads(next(iter(build_transfer_handover(result, evidence, scan_summary=summary).values())))
        assert len(payload['evidence']) == 1
        assert payload['manifest']['scan_status'] == 'COMPLETED_WITH_ERRORS'
    finally:
        services['connection'].close()


def test_background_job_finishes_despite_nus_block(tmp_path, monkeypatch):
    services = setup_services(tmp_path, monkeypatch, ScanError)
    job, ended = ScanJob(), Event()
    original = job._run
    def run(services):
        try:
            original(services)
        finally:
            ended.set()
    monkeypatch.setattr(job, '_run', run)
    try:
        assert job.start(services, 3)
        assert ended.wait(5)
        assert job.snapshot()['stage'] == 'finished'
        assert job.snapshot()['completed'] == 3
        assert job.snapshot()['error'] is None
        assert services['scan_repository'].count_evidence() == 1
    finally:
        services['connection'].close()


def test_database_failure_is_not_misreported_as_blocked_website(tmp_path, monkeypatch):
    services = setup_services(tmp_path, monkeypatch, ScanError)
    def broken_write(evidence):
        raise sqlite3.OperationalError('database unavailable')
    monkeypatch.setattr(services['scan_repository'], 'add_evidence', broken_write)
    try:
        with pytest.raises(sqlite3.OperationalError):
            services['scan_workflow'].run()
    finally:
        services['connection'].close()
