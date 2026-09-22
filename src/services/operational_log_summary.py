"""Summarise backend operational JSONL logs for IT troubleshooting."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ERROR_EVENT_HINTS = ("error", "failed", "parse_error", "empty_response")


def summarise_operational_log(log_path: Path, recent_limit: int = 10) -> dict[str, Any]:
    """Return a compact, JSON-safe summary of an operational JSONL log."""
    if not log_path.exists():
        return {
            "log_path": str(log_path),
            "exists": False,
            "total_events": 0,
            "event_counts": {},
            "scan_summary": {},
            "llm_usage": {},
            "source_outcomes": [],
            "recent_attention_events": [],
            "invalid_line_count": 0,
        }

    event_counts: Counter[str] = Counter()
    scan_summary: dict[str, Any] = {
        "scan_started": 0,
        "scan_completed": 0,
        "sources_started": 0,
        "sources_completed": 0,
        "sources_failed": 0,
        "evidence_stored": 0,
    }
    llm_usage: dict[str, Any] = {
        "request_events": 0,
        "response_events": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }
    recent_attention_events: list[dict[str, Any]] = []
    source_outcomes: dict[str, dict[str, Any]] = {}
    invalid_line_count = 0
    first_timestamp: str | None = None
    last_timestamp: str | None = None

    with log_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                invalid_line_count += 1
                continue
            event_type = str(record.get("event_type", "unknown"))
            timestamp = str(record.get("timestamp", ""))
            payload = record.get("payload", {})
            event_counts[event_type] += 1
            first_timestamp = first_timestamp or timestamp
            last_timestamp = timestamp or last_timestamp
            _update_scan_summary(scan_summary, event_type, payload)
            _update_source_outcomes(source_outcomes, event_type, payload, timestamp)
            _update_llm_usage(llm_usage, event_type, payload)
            if _needs_attention(event_type):
                recent_attention_events.append(_compact_attention_event(record))
                recent_attention_events = recent_attention_events[-recent_limit:]

    return {
        "log_path": str(log_path),
        "exists": True,
        "first_timestamp": first_timestamp,
        "last_timestamp": last_timestamp,
        "total_events": sum(event_counts.values()),
        "event_counts": dict(sorted(event_counts.items())),
        "scan_summary": scan_summary,
        "llm_usage": llm_usage,
        "source_outcomes": _source_outcome_rows(source_outcomes),
        "recent_attention_events": recent_attention_events,
        "invalid_line_count": invalid_line_count,
    }


def _update_scan_summary(summary: dict[str, Any], event_type: str, payload: Any) -> None:
    """Accumulate scan/source/evidence counts from known event payloads."""
    payload = payload if isinstance(payload, dict) else {}
    if event_type == "scan_started":
        summary["scan_started"] += 1
    elif event_type == "scan_completed":
        summary["scan_completed"] += 1
        summary["evidence_stored"] += _safe_count(payload.get("evidence_count") or payload.get("stored_evidence_count") or payload.get("evidence"))
    elif event_type == "source_scan_started":
        summary["sources_started"] += 1
    elif event_type == "source_scan_completed":
        summary["sources_completed"] += 1
        summary["evidence_stored"] += _safe_count(payload.get("stored_evidence_count") or payload.get("evidence_count") or payload.get("evidence"))
    elif event_type == "source_scan_failed":
        summary["sources_failed"] += 1


def _update_source_outcomes(outcomes: dict[str, dict[str, Any]], event_type: str, payload: Any, timestamp: str) -> None:
    """Accumulate per-source scan outcomes for IT troubleshooting."""
    payload = payload if isinstance(payload, dict) else {}
    if event_type not in {"source_scan_started", "source_scan_completed", "source_scan_failed", "source_urls_discovered"}:
        return
    source_name = str(payload.get("source_name") or payload.get("source") or payload.get("organisation") or "Unknown source")
    row = outcomes.setdefault(
        source_name,
        {
            "source": source_name,
            "started": 0,
            "completed": 0,
            "failed": 0,
            "urls_discovered": 0,
            "evidence_stored": 0,
            "last_timestamp": "",
            "last_error": "",
        },
    )
    row["last_timestamp"] = timestamp or row["last_timestamp"]
    if event_type == "source_scan_started":
        row["started"] += 1
    elif event_type == "source_scan_completed":
        row["completed"] += 1
        row["evidence_stored"] += _safe_count(payload.get("stored_evidence_count") or payload.get("evidence_count") or payload.get("evidence"))
    elif event_type == "source_scan_failed":
        row["failed"] += 1
        row["last_error"] = payload.get("error") or payload.get("reason") or payload.get("status") or "Failed without detailed error"
    elif event_type == "source_urls_discovered":
        row["urls_discovered"] += _safe_count(payload.get("url_count") or payload.get("discovered_url_count") or payload.get("urls_discovered") or payload.get("count"))


def _safe_count(value: Any) -> int:
    """Convert legacy/optional log counts without breaking IT diagnostics."""
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _source_outcome_rows(outcomes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Return per-source outcomes sorted by failed/low-yield sources first."""
    return sorted(
        outcomes.values(),
        key=lambda row: (
            0 if row.get("failed", 0) else 1,
            int(row.get("evidence_stored", 0)),
            str(row.get("source", "")),
        ),
    )


def _update_llm_usage(summary: dict[str, Any], event_type: str, payload: Any) -> None:
    """Accumulate rough LLM request/response and token counts when available."""
    payload = payload if isinstance(payload, dict) else {}
    if event_type.startswith("llm_") and "request" in event_type:
        summary["request_events"] += 1
    if event_type.startswith("llm_") and ("response" in event_type or event_type.endswith("_completed")):
        summary["response_events"] += 1
    usage = payload.get("usage") or payload.get("token_usage") or {}
    if not isinstance(usage, dict):
        return
    input_tokens = _safe_count(usage.get("input_tokens") or usage.get("prompt_tokens"))
    output_tokens = _safe_count(usage.get("output_tokens") or usage.get("completion_tokens"))
    total_tokens = _safe_count(usage.get("total_tokens")) or input_tokens + output_tokens
    summary["input_tokens"] += input_tokens
    summary["output_tokens"] += output_tokens
    summary["total_tokens"] += total_tokens


def _needs_attention(event_type: str) -> bool:
    """Return whether an event should appear in the recent attention list."""
    lowered = event_type.lower()
    return any(hint in lowered for hint in ERROR_EVENT_HINTS)


def _compact_attention_event(record: dict[str, Any]) -> dict[str, Any]:
    """Keep attention events compact enough for safe terminal review."""
    payload = record.get("payload", {})
    payload = payload if isinstance(payload, dict) else {}
    return {
        "timestamp": record.get("timestamp"),
        "event_type": record.get("event_type"),
        "source": payload.get("source_name") or payload.get("source") or payload.get("organisation"),
        "error": payload.get("error") or payload.get("reason") or payload.get("status"),
    }
