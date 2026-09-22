"""Scan execution page."""
import json
from datetime import datetime

import streamlit as st
from src.core.exceptions import ScanError, RecommendationError
from src.dashboard.recommendations import _recommendation_summary_csv, _source_maintenance_advice_summary
from src.llm.fallback_recovery import fallback_recovery_result_payload
from src.models.domain import FallbackRecovery
from src.services.source_health_service import FALLBACK_READINESS_FILTER_OPTIONS, automatic_fallback_queue, filter_fallback_candidates, filter_source_health_rows, fallback_prompt_markdown, fallback_prompt_payload, fallback_readiness_counts, source_access_limits_note, source_fallback_candidates, source_health_rows, source_health_status_counts


def _strategy_label(source) -> str:
    source_type = source.source_type.value if hasattr(source.source_type, "value") else str(source.source_type)
    source_role = source.source_role.value if hasattr(source.source_role, "value") else str(source.source_role)
    source_family = source.source_family.value if hasattr(source, "source_family") and hasattr(source.source_family, "value") else str(getattr(source, "source_family", ""))
    if source_type == "FRAMEWORK":
        return "framework extraction"
    if source_type == "CATALOGUE":
        return "catalogue extraction"
    if source_type == "INDEX":
        return "bounded index traversal"
    if source_type == "TREND":
        return "trend / signal extraction"
    if source_role == "TREND_VALIDATION":
        return "signal validation"
    if source_family == "GOVERNMENT_AGENCY":
        return "official source scan"
    if source_family == "HIGHER_LEARNING":
        return "learning / research scan"
    return "article / publication scan"


def _source_type_badge(source_type: str) -> str:
    value = (source_type or "").upper()
    if value == "FRAMEWORK":
        return "🟢 framework"
    if value == "CATALOGUE":
        return "🔵 catalogue"
    if value == "INDEX":
        return "🟣 index"
    if value == "TREND":
        return "🟠 trend"
    return "⚪ article"


def _source_role_badge(source_role: str) -> str:
    value = (source_role or "").upper()
    if value == "PRIMARY_DISCOVERY":
        return "🟦 primary"
    if value == "SUPPORTING_DISCOVERY":
        return "🟨 supporting"
    if value == "TREND_VALIDATION":
        return "🟥 trend-check"
    return "⚪ role"


def _source_family_badge(source_family: str) -> str:
    value = (source_family or "").upper()
    if value == "PROFESSIONAL_BODY":
        return "🟢 professional body"
    if value == "HIGHER_LEARNING":
        return "🔵 higher learning"
    if value == "GOVERNMENT_AGENCY":
        return "🟣 government agency"
    return "⚪ source family"


def _badge_source_health_rows(rows: list[dict]) -> list[dict]:
    """Return display rows with source-family/type/role badges."""
    display_rows = []
    for row in rows:
        display_row = dict(row)
        display_row["Source family"] = _source_family_badge(str(row.get("Source family", "")))
        display_row["Source type"] = _source_type_badge(str(row.get("Source type", "")))
        display_row["Source role"] = _source_role_badge(str(row.get("Source role", "")))
        display_rows.append(display_row)
    return display_rows


def _badge_fallback_candidate_rows(rows: list[dict]) -> list[dict]:
    """Return fallback-candidate rows with source-family/type/role badges."""
    display_rows = []
    for row in rows:
        display_row = dict(row)
        display_row["Source family"] = _source_family_badge(str(row.get("Source family", "")))
        display_row["Source type"] = _source_type_badge(str(row.get("Source type", "")))
        display_row["Source role"] = _source_role_badge(str(row.get("Source role", "")))
        display_rows.append(display_row)
    return display_rows


def _fallback_candidate_label(row: dict) -> str:
    """Return a compact label for selecting one fallback candidate."""
    return f"{row.get('Organisation', 'Unknown')} · {row.get('Source', 'Unknown')} · {row.get('Recovery readiness', 'Unknown')}"


def _render_run_source_health(run, services: dict) -> None:
    """Show immediate source-health feedback for the completed scan."""
    if run.id is None:
        return
    evidence = services["scan_repository"].list_evidence_for_run(run.id)
    source_lookup = {source.id: source for source in services["source_repository"].list_all() if source.id is not None}
    health_rows = _badge_source_health_rows(source_health_rows(run, evidence, source_lookup))
    if not health_rows:
        return
    st.subheader("Source health from this scan")
    st.info(source_access_limits_note())
    health_counts = source_health_status_counts(health_rows)
    health_left, health_middle_left, health_middle_right, health_right = st.columns(4)
    health_left.metric("Healthy sources", health_counts["Healthy"])
    health_middle_left.metric("Low evidence", health_counts["Low evidence"])
    health_middle_right.metric("No evidence", health_counts["No evidence"])
    health_right.metric("Errors", health_counts["Error"])
    health_status_choice = st.selectbox(
        "Filter source health by status",
        ["All statuses", "Error", "No evidence", "Low evidence", "Healthy"],
        key=f"run_source_health_status_{run.id}",
    )
    visible_health_rows = filter_source_health_rows(health_rows, health_status_choice)
    st.dataframe(visible_health_rows, hide_index=True, width="stretch")
    st.download_button(
        "Download source health (CSV)",
        data=_recommendation_summary_csv(visible_health_rows),
        file_name=f"source_health_batch_{run.id}.csv",
        mime="text/csv",
    )
    st.caption("Sources with errors, no evidence, or low output are flagged for manual URL review in Recommendations and History.")


def render(services: dict) -> None:
    """Render explicit officer-controlled scan action."""
    st.header("Run Scan")
    sources = [source for source in services["source_repository"].list_enabled()]
    if sources:
        st.subheader("Crawler strategy overview")
        rows = []
        for source in sources:
            rows.append(
                {
                    "Organisation": source.organisation,
                    "Source": source.name,
                    "Family": source.source_family.value.replace("_", " ").title(),
                    "Type": source.source_type.value.title(),
                    "Role": source.source_role.value.replace("_", " ").title(),
                    "Strategy": _strategy_label(source),
                }
            )
        st.dataframe(rows, hide_index=True, width="stretch")
    scan_only = st.checkbox("Scan evidence only without running AI recommendation", value=True)

    if st.button("Run enabled source scan", type="primary"):
        try:
            progress_placeholder = st.empty()
            progress_bar = st.progress(0)
            source_index = {"value": 0}
            stage_labels = {
                "start": "discovering",
                "discovered": "scanning",
                "done": "done",
                "error": "error",
            }

            def _update_progress(index: int, total: int, source_name: str, source_family: str, source_type: str, phase: str) -> None:
                if total <= 0:
                    return
                if phase == "start":
                    source_index["value"] = index - 1
                elif phase in {"discovered", "done"}:
                    source_index["value"] = index
                percentage = source_index["value"] / total
                progress_bar.progress(min(1.0, percentage))
                source_label = f"{source_family.replace('_', ' ').title()} · {source_type.lower()}"
                if phase == "start":
                    progress_placeholder.info(f"{stage_labels[phase].title()} {source_name} [{source_label}] ({index} of {total})")
                elif phase == "discovered":
                    progress_placeholder.info(f"{stage_labels[phase].title()} {source_name} [{source_label}] ({index} of {total}) - links found")
                elif phase == "done":
                    progress_placeholder.info(f"Finished {source_name} [{source_label}] ({index} of {total})")
                else:
                    progress_placeholder.warning(f"Source failed: {source_name} [{source_label}] ({index} of {total})")

            with st.spinner("Discovering and scanning approved articles..."):
                run = services["scan_workflow"].run(progress_callback=_update_progress)
            progress_bar.progress(1.0)
            progress_placeholder.success("Scan finished.")
            st.success(f"Scan {run.status.value.lower().replace('_', ' ')}.")
            if run.error_summary:
                st.warning(run.error_summary)
            if run.id is not None:
                st.session_state["selected_scan_run_id"] = run.id
                _render_run_source_health(run, services)
            if not scan_only and run.id is not None:
                with st.spinner("Generating recommendations for this scan batch..."):
                    count = services["recommendation_workflow"].run(run.id)
                st.success(f"Generated {count} recommendation(s) for this scan batch.")
        except (ScanError, RecommendationError) as error:
            st.error(str(error))
