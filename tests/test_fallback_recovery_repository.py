"""Tests for persisted LLM fallback recovery records."""
import json
from datetime import datetime

from src.core.database import connect, initialise
from src.models.domain import FallbackRecovery, ScanStatus
from src.repositories.fallback_recovery_repository import FallbackRecoveryRepository
from src.repositories.scan_repository import ScanRepository


def test_fallback_recovery_repository_stores_records_separately_from_evidence(tmp_path) -> None:
    """LLM-recovered fallback outputs are auditable without becoming crawler evidence."""
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    scans = ScanRepository(connection)
    run = scans.create_run(datetime.now().astimezone(), [])
    completed = scans.complete_run(run, ScanStatus.COMPLETED, None)
    repository = FallbackRecoveryRepository(connection)

    stored = repository.add(
        FallbackRecovery(
            None,
            completed.id,
            "Org A Catalogue",
            "Org A",
            "https://a.example/catalogue",
            "COMPLETED",
            1,
            json.dumps({"recovered_items": [{"title": "Course"}]}),
            datetime.now().astimezone(),
        )
    )

    rows = repository.list_for_scan_run(completed.id or 0)

    assert stored.id is not None
    assert rows[0].source_name == "Org A Catalogue"
    assert rows[0].recovered_item_count == 1
    assert json.loads(rows[0].raw_result)["recovered_items"][0]["title"] == "Course"
    assert scans.count_evidence() == 0


def test_fallback_recovery_repository_updates_raw_result_for_verification(tmp_path) -> None:
    """URL verification metadata can be persisted on the original recovery record."""
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    scans = ScanRepository(connection)
    run = scans.create_run(datetime.now().astimezone(), [])
    completed = scans.complete_run(run, ScanStatus.COMPLETED, None)
    repository = FallbackRecoveryRepository(connection)
    stored = repository.add(
        FallbackRecovery(
            None,
            completed.id,
            "Org A Catalogue",
            "Org A",
            "https://a.example/catalogue",
            "COMPLETED",
            1,
            json.dumps({"recovered_items": [{"title": "Course"}]}),
            datetime.now().astimezone(),
        )
    )

    repository.update_raw_result(stored.id or 0, json.dumps({"verification_summary": {"✅ Verified by URL": 1}}))

    rows = repository.list_for_scan_run(completed.id or 0)
    assert json.loads(rows[0].raw_result)["verification_summary"]["✅ Verified by URL"] == 1
