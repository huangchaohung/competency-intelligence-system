from datetime import datetime
from src.core.database import connect, initialise
from src.models.domain import Evidence, Source
from src.repositories.scan_repository import ScanRepository
from src.repositories.source_repository import SourceRepository


def test_evidence_round_trip(tmp_path) -> None:
    """Clean evidence retains provenance after persistence."""
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    source = SourceRepository(connection).upsert(Source(None, "Test", "https://example.com", "Test Org", "Unknown"))
    repository = ScanRepository(connection)
    run = repository.create_run(datetime.now().astimezone())
    saved = repository.add_evidence(Evidence(None, run.id or 0, source.id or 0, "Article", "Useful evidence title", None, "Test Org", "https://example.com/a", "Useful evidence text " * 10, datetime.now().astimezone(), "INFERRED"))
    assert repository.list_evidence()[0] == saved
