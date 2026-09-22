"""Home dashboard page."""
import streamlit as st
from collections import Counter
import csv
from io import StringIO
from src.services.source_health_service import source_health_rows, source_health_status_counts


def _fmt(dt_value) -> str:
    return dt_value.strftime("%Y-%m-%d %H:%M") if dt_value else "Unknown"


def _sources_needing_attention(rows: list[dict]) -> list[dict]:
    """Return source-health rows that may need source tuning or fallback review."""
    return [row for row in rows if row.get("Status") != "Healthy"]


def _attention_rows_csv(rows: list[dict]) -> str:
    """Return latest-scan attention rows as CSV text."""
    if not rows:
        return ""
    fieldnames = ["Status", "Evidence items", "Organisation", "Source", "Suggested action"]
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows({field: row.get(field, "") for field in fieldnames} for row in rows)
    return buffer.getvalue()


def _validation_checkpoint(latest_run=None, latest_evidence: list | None = None, health_rows: list[dict] | None = None) -> dict:
    """Return the next practical validation checkpoint for the prototype."""
    if latest_run is None:
        return {
            "Checkpoint": "Open Streamlit for UIUX review",
            "Why": "No scan has been recorded yet, so first check navigation, source configuration, and framework import.",
            "Suggested action": "Open Streamlit and review Home, Source Configuration, and Current Framework before running a full scan.",
        }
    latest_evidence = latest_evidence or []
    health_rows = health_rows or []
    if not latest_evidence:
        return {
            "Checkpoint": "Run a full source scan",
            "Why": "The latest scan has no retained evidence, so output quality cannot be assessed yet.",
            "Suggested action": "Open Run Scan and run enabled sources. If sources fail, review source health and fallback candidates.",
        }
    problem_sources = [row for row in health_rows if row.get("Status") in {"Error", "No evidence"}]
    if problem_sources:
        return {
            "Checkpoint": "Review source quality and fallback candidates",
            "Why": f"{len(problem_sources)} enabled source(s) had errors or no retained evidence.",
            "Suggested action": "Open Run Scan or History, inspect source health, then decide whether to tune URLs or run controlled fallback recovery for selected sources.",
        }
    if getattr(latest_run, "status", None) and latest_run.status.value == "COMPLETED_WITH_ERRORS":
        return {
            "Checkpoint": "Review scan errors",
            "Why": "The latest scan stored evidence but completed with errors.",
            "Suggested action": "Open History and compare source-health errors against the batch evidence before generating or trusting recommendations.",
        }
    return {
        "Checkpoint": "Open Streamlit for recommendation and UIUX review",
        "Why": "The latest scan has retained evidence and no major empty/error source signals.",
        "Suggested action": "Open Recommendations and History to check organised scan quality, recommendation support breadth, exports, Ask AI, and page responsiveness.",
    }


def render(services: dict) -> None:
    """Render the prototype overview."""
    st.title("STE Competency Intelligence")
    st.info("Human-governed prototype: evidence is collected for review; the framework is never updated automatically.")
    st.write("Configure approved public sources, run an HTML scan, inspect the evidence, then generate recommendations.")
    sources = services["source_repository"].list_all()
    scan_repo = services["scan_repository"]
    runs = scan_repo.list_runs(limit=5)
    first, second = st.columns(2)
    first.metric("Configured sources", len(sources))
    second.metric("Enabled sources", sum(source.enabled for source in sources))
    if runs:
        latest = runs[0]
        latest_evidence = scan_repo.list_evidence_for_run(latest.id or 0)
        st.subheader("Latest scan summary")
        summary_left, summary_right = st.columns(2)
        summary_left.metric("Articles stored in latest scan", len(latest_evidence))
        summary_right.metric("Status", latest.status.value.replace("_", " ").title())
        st.caption(f"Latest scan: {_fmt(latest.started_at)}")
        if latest.error_summary:
            st.warning(latest.error_summary)
        source_lookup = {source.id: source for source in sources if source.id is not None}
        health_rows = source_health_rows(latest, latest_evidence, source_lookup)
        checkpoint = _validation_checkpoint(latest, latest_evidence, health_rows)
        st.subheader("Suggested validation checkpoint")
        st.info(f"{checkpoint['Checkpoint']}: {checkpoint['Why']}")
        st.caption(checkpoint["Suggested action"])
        if health_rows:
            health_counts = source_health_status_counts(health_rows)
            health_left, health_middle_left, health_middle_right, health_right = st.columns(4)
            health_left.metric("Healthy sources", health_counts["Healthy"])
            health_middle_left.metric("Low evidence", health_counts["Low evidence"])
            health_middle_right.metric("No evidence", health_counts["No evidence"])
            health_right.metric("Errors", health_counts["Error"])
            attention_rows = _sources_needing_attention(health_rows)
            if attention_rows:
                st.subheader("Sources needing attention")
                st.dataframe(
                    [
                        {
                            "Status": row["Status"],
                            "Evidence items": row["Evidence items"],
                            "Organisation": row["Organisation"],
                            "Source": row["Source"],
                            "Suggested action": row["Suggested action"],
                        }
                        for row in attention_rows
                    ],
                    hide_index=True,
                    width="stretch",
                )
                st.download_button(
                    "Download attention list (CSV)",
                    data=_attention_rows_csv(attention_rows),
                    file_name=f"sources_needing_attention_{latest.id or 0}.csv",
                    mime="text/csv",
                )
        if latest_evidence:
            source_counts = Counter()
            for item in latest_evidence:
                source_counts[item.organisation] += 1
            st.dataframe(
                [{"Source": organisation, "Evidence items": count} for organisation, count in source_counts.most_common()],
                hide_index=True,
                width="stretch",
            )
        recent_runs = [
            {
                "Started": _fmt(run.started_at),
                "Status": run.status.value.replace("_", " ").title(),
                "Evidence": len(scan_repo.list_evidence_for_run(run.id or 0)),
                "Errors": run.error_summary or "None",
            }
            for run in runs
        ]
        st.subheader("Recent scans")
        st.dataframe(recent_runs, hide_index=True, width="stretch")
    else:
        checkpoint = _validation_checkpoint()
        st.subheader("Suggested validation checkpoint")
        st.info(f"{checkpoint['Checkpoint']}: {checkpoint['Why']}")
        st.caption(checkpoint["Suggested action"])
