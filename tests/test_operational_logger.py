"""Tests for backend-only operational logging."""
import json

from src.services.operational_logger import OperationalLogger


def test_operational_logger_writes_jsonl_events(tmp_path) -> None:
    """Each backend event is written as a timestamped JSON object."""
    logger = OperationalLogger(tmp_path)

    logger.event("scan_started", {"scan_run_id": 7, "enabled_source_count": 3})

    rows = [json.loads(line) for line in (tmp_path / "operational_audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert rows[0]["event_type"] == "scan_started"
    assert rows[0]["payload"]["scan_run_id"] == 7
    assert rows[0]["payload"]["enabled_source_count"] == 3
    assert "timestamp" in rows[0]


def test_operational_logger_redacts_likely_secrets(tmp_path) -> None:
    """API keys, tokens, and auth-like fields must not be written to logs."""
    logger = OperationalLogger(tmp_path)

    logger.event(
        "llm_request",
        {
            "api_key": "sk-test123456789abcdef",
            "headers": {"Authorization": "Bearer abc.def.ghi"},
            "prompt": "safe text with sk-test123456789abcdef inside",
        },
    )

    text = (tmp_path / "operational_audit.jsonl").read_text(encoding="utf-8")
    assert "sk-test" not in text
    assert "Bearer abc" not in text
    row = json.loads(text)
    assert row["payload"]["api_key"] == "[REDACTED]"
    assert row["payload"]["headers"]["Authorization"] == "[REDACTED]"
    assert "[REDACTED]" in row["payload"]["prompt"]


def test_operational_logger_keeps_usage_metadata_while_redacting_secrets(tmp_path) -> None:
    """Token usage is useful for IT/cost review and should not be mistaken for a secret."""
    logger = OperationalLogger(tmp_path)

    logger.event("llm_response", {"token_usage": {"input_tokens": 100, "output_tokens": 20}, "access_token": "secret-token"})

    row = json.loads((tmp_path / "operational_audit.jsonl").read_text(encoding="utf-8"))
    assert row["payload"]["token_usage"]["input_tokens"] == 100
    assert row["payload"]["access_token"] == "[REDACTED]"


def test_operational_logger_rotates_large_jsonl_files(tmp_path) -> None:
    """Backend logs should not grow forever in a long-running prototype."""
    active_log = tmp_path / "operational_audit.jsonl"
    active_log.write_text("x" * 80, encoding="utf-8")
    logger = OperationalLogger(tmp_path, max_bytes=50, backup_count=2)

    logger.event("after_rotation", {"safe": True})

    assert (tmp_path / "operational_audit.jsonl.1").exists()
    assert len((tmp_path / "operational_audit.jsonl").read_text(encoding="utf-8").splitlines()) == 1
    row = json.loads((tmp_path / "operational_audit.jsonl").read_text(encoding="utf-8"))
    assert row["event_type"] == "after_rotation"
