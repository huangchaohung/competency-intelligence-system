"""Tests for backend operational log summaries."""
from __future__ import annotations

from src.services.operational_logger import OperationalLogger
from src.services.operational_log_summary import summarise_operational_log


def test_operational_log_summary_counts_events_and_attention(tmp_path) -> None:
    """IT summary should highlight scan counts and recent failures."""
    logger = OperationalLogger(tmp_path)
    logger.event("scan_started", {"scan_run_id": 1})
    logger.event("source_scan_started", {"source_name": "IEEE"})
    logger.event("source_urls_discovered", {"source_name": "IEEE", "url_count": 30})
    logger.event("source_scan_completed", {"source_name": "IEEE", "stored_evidence_count": 25})
    logger.event("source_scan_failed", {"source_name": "Blocked Source", "error": "403 Client Error"})
    logger.event("llm_recommendation_request", {"model": "test"})
    logger.event("llm_recommendation_response", {"usage": {"input_tokens": 100, "output_tokens": 25}})

    summary = summarise_operational_log(logger.path)

    assert summary["exists"] is True
    assert summary["total_events"] == 7
    assert summary["event_counts"]["source_scan_failed"] == 1
    assert summary["scan_summary"]["sources_completed"] == 1
    assert summary["scan_summary"]["sources_failed"] == 1
    assert summary["scan_summary"]["evidence_stored"] == 25
    assert summary["source_outcomes"][0]["source"] == "Blocked Source"
    assert summary["source_outcomes"][0]["failed"] == 1
    assert summary["source_outcomes"][1]["source"] == "IEEE"
    assert summary["source_outcomes"][1]["urls_discovered"] == 30
    assert summary["source_outcomes"][1]["evidence_stored"] == 25
    assert summary["llm_usage"]["request_events"] == 1
    assert summary["llm_usage"]["response_events"] == 1
    assert summary["llm_usage"]["total_tokens"] == 125
    assert summary["recent_attention_events"][0]["source"] == "Blocked Source"


def test_operational_log_summary_handles_missing_log(tmp_path) -> None:
    """Missing logs should produce a clear empty summary."""
    summary = summarise_operational_log(tmp_path / "missing.jsonl")

    assert summary["exists"] is False
    assert summary["total_events"] == 0
    assert summary["event_counts"] == {}
    assert summary["source_outcomes"] == []


def test_operational_log_summary_accepts_legacy_count_aliases_and_bad_values(tmp_path) -> None:
    """Older or imperfect log payloads must not break the IT summary."""
    logger = OperationalLogger(tmp_path)
    logger.event("source_urls_discovered", {"source": "Legacy", "urls_discovered": "12"})
    logger.event("source_scan_completed", {"source": "Legacy", "evidence": "not-a-number"})
    logger.event("llm_recommendation_response", {"usage": {"prompt_tokens": "bad", "completion_tokens": 4}})

    summary = summarise_operational_log(logger.path)
    row = summary["source_outcomes"][0]
    assert row["source"] == "Legacy"
    assert row["urls_discovered"] == 12
    assert row["evidence_stored"] == 0
    assert summary["llm_usage"]["input_tokens"] == 0
    assert summary["llm_usage"]["output_tokens"] == 4
    assert summary["llm_usage"]["total_tokens"] == 4
