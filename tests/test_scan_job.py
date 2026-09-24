from threading import Event, Lock
from src.services.scan_job import ScanJob


def test_worker_reports_progress_and_prevents_duplicate(monkeypatch):
    from src.services import session_workspace
    cleared = []
    monkeypatch.setattr(session_workspace, 'clear_current_scan', lambda services: cleared.append(True))
    started, release, finished = Event(), Event(), Event()
    class Workflow:
        def run(self, progress_callback):
            progress_callback(1, 2, 'Source A', '', '', 'done')
            progress_callback(2, 2, 'Source B', '', '', 'start')
            started.set()
            assert release.wait(5)
            progress_callback(2, 2, 'Source B', '', '', 'error')
    job = ScanJob()
    original = job._run
    def wrapped(services):
        try:
            original(services)
        finally:
            finished.set()
    monkeypatch.setattr(job, '_run', wrapped)
    services = {'lock': Lock(), 'scan_workflow': Workflow()}
    assert job.start(services, 2)
    try:
        assert started.wait(5)
        assert job.snapshot()['completed'] == 1
        assert job.snapshot()['source'] == 'Source B'
        assert not job.start(services, 2)
    finally:
        release.set()
    assert finished.wait(5)
    assert job.snapshot()['completed'] == 2
    assert not job.snapshot()['running']
    assert not services['lock'].locked()
    assert cleared == [True]


def test_worker_failure_unlocks_and_remains_retryable(monkeypatch):
    from src.services import session_workspace
    monkeypatch.setattr(session_workspace, 'clear_current_scan', lambda services: None)
    class Workflow:
        def run(self, progress_callback):
            raise ValueError('test failure')
    services = {'lock': Lock(), 'scan_workflow': Workflow()}
    job = ScanJob()
    job._run(services)
    assert job.snapshot()['stage'] == 'failed'
    assert 'test failure' in job.snapshot()['error']
    assert not job.snapshot()['running']
    assert not services['lock'].locked()
