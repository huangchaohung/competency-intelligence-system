from datetime import datetime
from src.core.database import connect, initialise
from src.models.domain import Evidence, ScanStatus, Source
from src.repositories.scan_repository import ScanRepository
from src.repositories.source_repository import SourceRepository


def test_scan_repository_reports_source_health(tmp_path) -> None:
    """Source health exposes evidence volume and recency for operations."""
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    source = SourceRepository(connection).upsert(Source(None, "Test", "https://example.com", "Test Org", "Unknown"))
    repository = ScanRepository(connection)
    run = repository.create_run(datetime.now().astimezone())
    extracted_at = datetime.now().astimezone()
    repository.add_evidence(Evidence(None, run.id or 0, source.id or 0, "Article", "Test article", None, "Test Org", "https://example.com/article", "Clean evidence text " * 10, extracted_at, "INFERRED"))
    health = repository.list_source_health()[source.id or 0]
    assert repository.count_evidence() == 1
    assert health.evidence_count == 1
    assert health.last_evidence_at == extracted_at
    assert repository.list_runs()[0].id == run.id


def test_scan_repository_clear_evidence_removes_all_rows(tmp_path) -> None:
    """A fresh scan can start from an empty evidence store."""
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    source = SourceRepository(connection).upsert(Source(None, "Test", "https://example.com", "Test Org", "Unknown"))
    repository = ScanRepository(connection)

    for index in range(6):
        run = repository.create_run(datetime.now().astimezone())
        repository.add_evidence(Evidence(None, run.id or 0, source.id or 0, "Article", f"Article {index}", None, "Test Org", f"https://example.com/{index}", "Clean evidence text " * 10, datetime.now().astimezone(), "INFERRED"))
        repository.complete_run(run, ScanStatus.COMPLETED, None)

    repository.clear_evidence()
    assert repository.count_evidence() == 0


def test_scan_repository_prunes_evidence_to_recent_runs(tmp_path) -> None:
    """Evidence retention keeps only the newest scan batches."""
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    source = SourceRepository(connection).upsert(Source(None, "Test", "https://example.com", "Test Org", "Unknown"))
    repository = ScanRepository(connection)

    runs = []
    for index in range(6):
        run = repository.create_run(datetime.now().astimezone())
        runs.append(run)
        repository.add_evidence(Evidence(None, run.id or 0, source.id or 0, "Article", f"Article {index}", None, "Test Org", f"https://example.com/{index}", "Clean evidence text " * 10, datetime.now().astimezone(), "INFERRED"))
        repository.complete_run(run, ScanStatus.COMPLETED, None)

    deleted = repository.prune_evidence_to_recent_runs(5)

    assert deleted == 1
    assert repository.count_evidence() == 5
    assert repository.list_evidence_for_run(runs[0].id or 0) == []
    assert len(repository.list_evidence_for_run(runs[-1].id or 0)) == 1
    assert repository.get_summary(runs[0].id)['evidence_count'] == 1


def test_summary_preserves_original_health_after_text_removed(tmp_path):
    connection = connect(tmp_path / 'test.db')
    initialise(connection)
    initialise(connection)  # existing databases can initialise repeatedly
    source = SourceRepository(connection).upsert(Source(None, 'Test', 'https://example.org', 'Org'))
    repo = ScanRepository(connection)
    run = repo.create_run(datetime.now().astimezone(), [{'id': source.id, 'name': source.name, 'url': source.url}])
    assert repo.get_summary(run.id) is None
    repo.add_evidence(Evidence(None, run.id, source.id, 'COURSE', 'Course', None, 'Org', 'https://example.org/course', 'text', datetime.now().astimezone()))
    repo.complete_run(run, ScanStatus.COMPLETED, None)
    before = repo.get_summary(run.id)
    repo.clear_evidence()
    assert repo.get_summary(run.id) == before
    assert before['health'][0]['Evidence items'] == 1
    assert before['health'][0]['Status'] == 'Low evidence'
    assert 'LLM fallback allowed' not in before['health'][0]
    connection.close()
