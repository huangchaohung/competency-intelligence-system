"""Create a compact Markdown maintenance report for IT handover."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from src.services.operational_log_summary import summarise_operational_log
from src.services.system_diagnostics import build_system_diagnostics


def build_maintenance_report(project_root: Path) -> str:
    """Return a Markdown report combining system diagnostics and log summary."""
    project_root = project_root.resolve()
    diagnostics = build_system_diagnostics(project_root)
    log_summary = summarise_operational_log(project_root / "logs" / "operational_audit.jsonl")
    lines = [
        "# STE Competency Intelligence Maintenance Report",
        "",
        f"Generated at: {_fmt_timestamp(datetime.now().astimezone().isoformat())}",
        "",
        "## Overall status",
        "",
        f"- Status: {diagnostics.get('overall_status', 'Unknown')}",
        f"- Project root: `{diagnostics.get('project_root', '')}`",
        f"- OpenAI API key configured: {_yes_no(diagnostics.get('configuration', {}).get('openai_api_key_configured'))}",
        f"- OpenAI model: `{diagnostics.get('configuration', {}).get('openai_model', 'Unknown')}`",
        "",
        "## Dependency check",
        "",
        *_dependency_lines(diagnostics.get("python_imports", {})),
        "",
        "## Configuration and database",
        "",
        f"- Source catalogue present: {_yes_no(diagnostics.get('configuration', {}).get('sources_yaml_exists'))}",
        f"- Framework template present: {_yes_no(diagnostics.get('configuration', {}).get('framework_template_exists'))}",
        f"- SQLite database present: {_yes_no(diagnostics.get('database', {}).get('exists'))}",
        f"- Latest schema migration: {diagnostics.get('database', {}).get('latest_migration') or 'Unknown'}",
        f"- Missing expected tables: {_join_or_none(diagnostics.get('database', {}).get('missing_expected_tables', []))}",
        "",
        "## Operational log summary",
        "",
        f"- Log exists: {_yes_no(log_summary.get('exists'))}",
        f"- Log path: `{log_summary.get('log_path', '')}`",
        f"- First event: {_fmt_timestamp(log_summary.get('first_timestamp'))}",
        f"- Last event: {_fmt_timestamp(log_summary.get('last_timestamp'))}",
        f"- Total events: {log_summary.get('total_events', 0)}",
        f"- Invalid JSONL lines: {log_summary.get('invalid_line_count', 0)}",
        "",
        "## Scan summary from logs",
        "",
        *_scan_summary_lines(log_summary.get("scan_summary", {})),
        "",
        "## Source outcomes from logs",
        "",
        *_source_outcome_lines(log_summary.get("source_outcomes", [])),
        "",
        "## LLM usage from logs",
        "",
        *_llm_usage_lines(log_summary.get("llm_usage", {})),
        "",
        "## Recent attention events",
        "",
        *_attention_lines(log_summary.get("recent_attention_events", [])),
        "",
        "## Notes for maintainers",
        "",
        "- This report is read-only and does not crawl websites or call OpenAI.",
        "- The report does not print API keys or secret values.",
        "- For deeper debugging, inspect `logs/operational_audit.jsonl` directly.",
    ]
    return "\n".join(lines) + "\n"


def _dependency_lines(imports: dict[str, bool]) -> list[str]:
    """Render dependency availability as Markdown bullets."""
    if not imports:
        return ["- No dependency information available."]
    return [f"- `{name}`: {_yes_no(available)}" for name, available in sorted(imports.items())]


def _scan_summary_lines(summary: dict[str, Any]) -> list[str]:
    """Render scan log summary as Markdown bullets."""
    if not summary:
        return ["- No scan summary available."]
    return [
        f"- Scans started: {summary.get('scan_started', 0)}",
        f"- Scans completed: {summary.get('scan_completed', 0)}",
        f"- Sources started: {summary.get('sources_started', 0)}",
        f"- Sources completed: {summary.get('sources_completed', 0)}",
        f"- Sources failed: {summary.get('sources_failed', 0)}",
        f"- Evidence stored: {summary.get('evidence_stored', 0)}",
    ]


def _source_outcome_lines(outcomes: list[dict[str, Any]]) -> list[str]:
    """Render compact per-source crawler outcomes for IT maintainers."""
    if not outcomes:
        return ["- No per-source outcome information available."]
    lines = ["| Source | Completed | Failed | URLs discovered | Evidence stored | Last error |", "| ------ | --------- | ------ | --------------- | --------------- | ---------- |"]
    for row in outcomes[:25]:
        lines.append(
            "| {source} | {completed} | {failed} | {urls} | {evidence} | {error} |".format(
                source=_markdown_table_text(row.get("source", "Unknown source")),
                completed=row.get("completed", 0),
                failed=row.get("failed", 0),
                urls=row.get("urls_discovered", 0),
                evidence=row.get("evidence_stored", 0),
                error=_markdown_table_text(row.get("last_error") or "-"),
            )
        )
    if len(outcomes) > 25:
        lines.append(f"- Showing first 25 of {len(outcomes)} source rows. Inspect `logs/operational_audit.jsonl` for the full backend trace.")
    return lines


def _llm_usage_lines(summary: dict[str, Any]) -> list[str]:
    """Render LLM usage summary as Markdown bullets."""
    if not summary:
        return ["- No LLM usage information available."]
    return [
        f"- Request events: {summary.get('request_events', 0)}",
        f"- Response events: {summary.get('response_events', 0)}",
        f"- Input tokens: {summary.get('input_tokens', 0)}",
        f"- Output tokens: {summary.get('output_tokens', 0)}",
        f"- Total tokens: {summary.get('total_tokens', 0)}",
    ]


def _attention_lines(events: list[dict[str, Any]]) -> list[str]:
    """Render recent attention events as compact Markdown bullets."""
    if not events:
        return ["- None recorded."]
    lines = []
    for event in events:
        source = event.get("source") or "Unknown source"
        error = event.get("error") or "No detail"
        lines.append(f"- {_fmt_timestamp(event.get('timestamp'))} · `{event.get('event_type', 'unknown')}` · {source}: {error}")
    return lines


def _yes_no(value: Any) -> str:
    """Render booleans as friendly yes/no labels."""
    return "Yes" if bool(value) else "No"


def _join_or_none(values: list[Any]) -> str:
    """Render a list compactly."""
    clean = [str(value) for value in values if value]
    return ", ".join(clean) if clean else "None"


def _markdown_table_text(value: Any) -> str:
    """Escape compact values for Markdown table cells."""
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _fmt_timestamp(value: Any) -> str:
    """Trim ISO timestamps to the project display convention where possible."""
    if not value:
        return "Unknown"
    return str(value)[:16].replace("T", " ")
