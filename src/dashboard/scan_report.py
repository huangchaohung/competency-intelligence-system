"""Unified batch history page."""
from collections import Counter, defaultdict
from datetime import datetime
from io import BytesIO
import json
import logging
from time import perf_counter
from openpyxl import Workbook
import streamlit as st
from src.dashboard.recommendations import _build_recommendation_pack, _fallback_recovery_payloads, _human_label, _question_history_csv, _question_history_markdown, _question_history_summary, _recommendation_pack_markdown, _recommendation_summary_csv, _source_maintenance_advice_summary, _support_coverage_rows
from src.services.fallback_provenance import fallback_provenance_label, fallback_verification_label
from src.services.fallback_verification_workflow import verify_recovery_record
from src.services.evidence_organiser import EvidenceOrganiser
from src.services.source_health_service import FALLBACK_READINESS_FILTER_OPTIONS, combined_source_maintenance_recommendations, filter_fallback_candidates, filter_source_health_rows, fallback_prompt_markdown, fallback_prompt_payload, fallback_readiness_counts, source_access_limits_note, source_fallback_candidates, source_health_action, source_health_rows, source_health_status_counts, source_maintenance_priority_counts, source_maintenance_recommendations as build_source_maintenance_recommendations

LOGGER = logging.getLogger(__name__)
HIDDEN_RECOMMENDATION_TYPES = {"ALREADY_COVERED", "INSUFFICIENT_EVIDENCE"}
ORGANISED_SCAN_BUCKETS = (
    ("competencies_or_standards", "Competencies / standards"),
    ("courses_programmes_or_resources", "Courses / resources"),
    ("research_reports_or_capability", "Research / capability"),
    ("signals_and_topics", "Signals / topics"),
)


def _fmt(dt_value) -> str:
    if isinstance(dt_value, str):
        dt_value = datetime.fromisoformat(dt_value[:19].replace("T", " "))
    return dt_value.strftime("%Y-%m-%d %H:%M") if dt_value else "Unknown"


def _preview(text: str, word_limit: int = 100) -> str:
    words = text.split()
    if len(words) <= word_limit:
        return text
    return " ".join(words[:word_limit]) + "..."


def _credibility_label(evidence_type: str) -> str:
    value = (evidence_type or "").lower()
    if "statistical report" in value or "workforce report" in value or "standard / competency guidance" in value:
        return "standards / reports"
    if "research journal" in value or "research journal / paper" in value or "official announcement" in value:
        return "official guidance / research"
    if "general article" in value or "news" in value:
        return "news / commentary"
    if "commentary" in value or "training / learning catalogue" in value:
        return "catalogue / training"
    return "news / commentary"


def _credibility_badge(label: str) -> str:
    value = (label or "").lower()
    if "standards / reports" in value:
        return "🟢"
    if "official guidance / research" in value:
        return "🔵"
    if "news / commentary" in value:
        return "🟠"
    return "⚪"


def _source_label(evidence_type: str) -> str:
    return _credibility_label(evidence_type)


def _evidence_type_label(evidence_type: str) -> str:
    value = (evidence_type or "").upper()
    if value == "EXPLICIT_COMPETENCY":
        return "explicit competency"
    if value == "COURSE":
        return "course"
    if value == "CERTIFICATION":
        return "certification"
    if value == "RESEARCH_CAPABILITY":
        return "research capability"
    if value == "TECHNOLOGY_TOPIC":
        return "technology topic"
    if value == "TREND_SIGNAL":
        return "trend signal"
    if value == "PROFESSIONAL_RESOURCE":
        return "professional resource"
    if value == "ARTICLE_TEXT":
        return "article text"
    return "unknown"


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


def _evidence_reference_payload(recommendation, evidence_by_id) -> list[dict]:
    references: list[dict] = []
    for evidence_id in recommendation.supporting_evidence_ids:
        evidence = evidence_by_id.get(evidence_id)
        if evidence:
            references.append(
                {
                    "id": evidence.id,
                    "title": evidence.title,
                    "organisation": evidence.organisation,
                    "evidence_type": evidence.evidence_type,
                    "source_label": _source_label(evidence.evidence_type),
                    "source_type": evidence_by_id.get(evidence.id).source_type.value if evidence_by_id.get(evidence.id) and hasattr(evidence_by_id.get(evidence.id), "source_type") else "Unknown",
                    "url": evidence.url,
                }
            )
        else:
            references.append({"id": evidence_id})
    return references


def _organised_scan_rows(organised_scan: dict) -> list[dict]:
    """Return compact officer-facing rows from an organised scan map."""
    rows = []
    for item in organised_scan.get("organisations", []):
        counts = item.get("counts", {})
        rows.append(
            {
                "Organisation": item.get("organisation", "Unknown"),
                "Competencies / standards": counts.get("competencies_or_standards", 0),
                "Courses / resources": counts.get("courses_programmes_or_resources", 0),
                "Research / capability": counts.get("research_reports_or_capability", 0),
                "Signals / topics": counts.get("signals_and_topics", 0),
                "Total": sum(int(value or 0) for value in counts.values()),
            }
        )
    return sorted(rows, key=lambda row: (-row["Total"], row["Organisation"]))


def _organised_scan_sample_rows(organisation_payload: dict, bucket: str) -> list[dict]:
    """Return representative item rows for one organised scan bucket."""
    return [
        {
            "Evidence ID": item.get("id"),
            "Title": item.get("title", "Untitled"),
            "Evidence type": _evidence_type_label(item.get("evidence_type", "")),
            "Evidence state": item.get("explicit_or_inferred", "Unknown"),
            "URL": item.get("url", ""),
            "Snippet": item.get("snippet", ""),
        }
        for item in organisation_payload.get(bucket, [])
    ]


def _enrich_organised_scan(organised_scan: dict, evidence: list, source_lookup: dict) -> dict:
    """Attach source metadata to an organised scan export without changing organiser behaviour."""
    evidence_lookup = {item.id: item for item in evidence if item.id is not None}
    enriched = json.loads(json.dumps(organised_scan))
    for organisation_payload in enriched.get("organisations", []):
        organisation_sources = [
            source_lookup[item.source_id]
            for item in evidence
            if item.organisation == organisation_payload.get("organisation") and item.source_id in source_lookup
        ]
        organisation_payload["source_metadata"] = {
            "countries": sorted({source.country for source in organisation_sources if source.country}),
            "source_families": sorted({source.source_family.value for source in organisation_sources}),
            "source_types": sorted({source.source_type.value for source in organisation_sources}),
            "source_roles": sorted({source.source_role.value for source in organisation_sources}),
        }
        for bucket, _label in ORGANISED_SCAN_BUCKETS:
            for item in organisation_payload.get(bucket, []):
                evidence_item = evidence_lookup.get(item.get("id"))
                source = source_lookup.get(evidence_item.source_id) if evidence_item else None
                item["source_metadata"] = (
                    {
                        "source_id": source.id,
                        "source_name": source.name,
                        "country": source.country,
                        "source_family": source.source_family.value,
                        "source_type": source.source_type.value,
                        "source_role": source.source_role.value,
                    }
                    if source
                    else {}
                )
    return enriched


def _source_health_rows(run, evidence: list, source_lookup: dict | None = None) -> list[dict]:
    """Summarise per-source output quality for the selected batch with dashboard badges."""
    rows = source_health_rows(run, evidence, source_lookup)
    for row in rows:
        row["Source family"] = _source_family_badge(str(row.get("Source family", "")))
        row["Source type"] = _source_type_badge(str(row.get("Source type", "")))
        row["Source role"] = _source_role_badge(str(row.get("Source role", "")))
    return rows


def _source_health_action(status: str, llm_allowed: bool) -> str:
    """Return a plain-language action suggestion for one source-health status."""
    return source_health_action(status, llm_allowed)


def _source_health_status_counts(rows: list[dict]) -> dict[str, int]:
    """Count source-health statuses for compact officer-facing metrics."""
    return source_health_status_counts(rows)


def _filter_source_health_rows(rows: list[dict], status_choice: str) -> list[dict]:
    """Filter source-health rows by status while preserving the full default view."""
    return filter_source_health_rows(rows, status_choice)


def _source_fallback_candidates(run, evidence: list, source_lookup: dict | None = None) -> list[dict]:
    """Return future LLM fallback candidates."""
    return source_fallback_candidates(run, evidence, source_lookup)


def _source_maintenance_recommendations(source_health: list[dict]) -> list[dict]:
    """Return source-link maintenance recommendations for historical review."""
    return build_source_maintenance_recommendations(source_health)


def _combined_source_maintenance_recommendations(source_health: list[dict], fallback_recoveries: list | None = None) -> list[dict]:
    """Return deterministic and LLM-assisted source-link maintenance recommendations."""
    return combined_source_maintenance_recommendations(source_health, fallback_recoveries)


def _badge_fallback_candidate_rows(rows: list[dict]) -> list[dict]:
    """Return future LLM fallback candidates with dashboard badges."""
    rows = [dict(row) for row in rows]
    for row in rows:
        row["Source family"] = _source_family_badge(str(row.get("Source family", "")))
        row["Source type"] = _source_type_badge(str(row.get("Source type", "")))
        row["Source role"] = _source_role_badge(str(row.get("Source role", "")))
    return rows


def _show_credibility_legend() -> None:
    st.info(
        "Credibility guide: 🟢 standards / reports are strongest; 🔵 official guidance / research is strong; "
        "🟠 news / commentary is moderate; ⚪ catalogue / training is softer."
    )


def _evidence_type_options(evidence: list) -> list[str]:
    values = sorted({_evidence_type_label(item.evidence_type) for item in evidence})
    return ["All evidence types"] + values


def _source_family_options(source_lookup: dict) -> list[str]:
    values = sorted({source.source_family.value.replace("_", " ").title() for source in source_lookup.values()})
    return ["All source families"] + values


def _source_type_options(source_lookup: dict) -> list[str]:
    values = sorted({source.source_type.value.replace("_", " ").title() for source in source_lookup.values()})
    return ["All source types"] + values


def _framework_xlsx_bytes(framework_snapshot: str) -> bytes:
    payload = json.loads(framework_snapshot or "{}")
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Framework"
    sheet.append(["Cap Area", "Sub-Functional Area", "Competency", "Definition"])
    for area in payload.get("sub_functional_areas", []):
        cap_area = area.get("cap_area", "")
        area_name = area.get("name", "")
        for competency in area.get("competencies", []):
            sheet.append([cap_area, area_name, competency.get("name", ""), competency.get("definition") or competency.get("description", "")])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _fallback_recovery_summary_rows(recoveries: list) -> list[dict]:
    """Return compact rows for saved LLM fallback recovery records."""
    rows = []
    for recovery in recoveries:
        try:
            payload = json.loads(getattr(recovery, "raw_result", "{}") or "{}")
        except json.JSONDecodeError:
            payload = {}
        rows.append(
            {
                "Record ID": recovery.id,
                "Created": _fmt(recovery.created_at),
                "Status": recovery.recovery_status.replace("_", " ").title(),
                "Provenance": fallback_provenance_label(),
                "Verification": payload.get("verification_summary") or fallback_verification_label(),
                "Organisation": recovery.organisation,
                "Source": recovery.source_name,
                "Recovered items": recovery.recovered_item_count,
                "Source advice": _source_maintenance_advice_summary(payload.get("source_maintenance_advice", {})),
                "Source URL": recovery.source_url,
            }
        )
    return rows


def _fallback_recovery_item_rows(recovery) -> list[dict]:
    """Return recovered item rows from one saved fallback recovery record."""
    try:
        payload = json.loads(getattr(recovery, "raw_result", "{}") or "{}")
    except json.JSONDecodeError:
        payload = {}
    rows = []
    for item in payload.get("recovered_items", []):
        rows.append(
            {
                "Title": item.get("title", "Untitled"),
                "Evidence class": str(item.get("evidence_class", "Unknown")).replace("_", " "),
                "Provenance": fallback_provenance_label(),
                "Verification": fallback_verification_label(item),
                "Evidence state": item.get("explicit_or_inferred", "Unknown"),
                "Confidence": f"{float(item.get('confidence', 0)):.0%}" if isinstance(item.get("confidence"), (float, int)) else "Unknown",
                "URL": item.get("url", ""),
                "Summary": item.get("summary", ""),
            }
        )
    return rows


def _fallback_recovery_export_payload(recoveries: list) -> list[dict]:
    """Return JSON-safe saved fallback recovery records for download."""
    export = []
    for recovery in recoveries:
        try:
            raw_result = json.loads(getattr(recovery, "raw_result", "{}") or "{}")
        except json.JSONDecodeError:
            raw_result = {"raw_result": getattr(recovery, "raw_result", "")}
        export.append(
            {
                "id": recovery.id,
                "scan_run_id": recovery.scan_run_id,
                "source_name": recovery.source_name,
                "organisation": recovery.organisation,
                "source_url": recovery.source_url,
                "provenance": fallback_provenance_label(),
                "verification_status": raw_result.get("verification_summary") or fallback_verification_label(),
                "recovery_status": recovery.recovery_status,
                "recovered_item_count": recovery.recovered_item_count,
                "created_at": recovery.created_at.isoformat(),
                "result": raw_result,
            }
        )
    return export


def _render_saved_fallback_recoveries(run, services: dict) -> bool:
    """Show saved LLM fallback recovery records attached to a scan batch."""
    repository = services.get("fallback_recovery_repository")
    if repository is None or run.id is None:
        return False
    recoveries = repository.list_for_scan_run(run.id)
    if not recoveries:
        return False
    st.subheader("LLM fallback recoveries")
    with st.expander("Saved LLM fallback recovery records", expanded=False):
        st.caption("🤖 LLM assisted · 🟡 Needs verification. These records came from explicit officer-triggered LLM fallback recovery. They remain separate from deterministic crawler evidence.")
        st.dataframe(_fallback_recovery_summary_rows(recoveries), hide_index=True, width="stretch")
        st.download_button(
            "Download saved fallback recoveries (JSON)",
            data=json.dumps(_fallback_recovery_export_payload(recoveries), indent=2),
            file_name=f"llm_fallback_recoveries_batch_{run.id or 0}.json",
            mime="application/json",
        )
        for recovery in recoveries:
            with st.expander(f"Recovery #{recovery.id} · {recovery.organisation} · {recovery.recovered_item_count} item(s)", expanded=False):
                st.caption(f"Source: {recovery.source_name} · {_fmt(recovery.created_at)}")
                item_rows = _fallback_recovery_item_rows(recovery)
                if item_rows:
                    st.dataframe(item_rows, hide_index=True, width="stretch")
                    if "fallback_url_verifier" in services:
                        if st.button(f"Verify recovered URLs for record #{recovery.id}", key=f"history_verify_fallback_{recovery.id}"):
                            with st.spinner("Verifying recovered URLs with deterministic fetches..."):
                                verify_recovery_record(
                                    recovery,
                                    services["fallback_url_verifier"],
                                    repository,
                                    services.get("operational_logger"),
                                )
                            st.success(f"Verification saved for fallback recovery record #{recovery.id}.")
                            st.rerun()
                else:
                    st.info("No recovered items were saved in this recovery record.")
    return True


def render(services: dict) -> None:
    """Render one historical batch with scan evidence and recommendations."""
    st.header("History")
    _show_credibility_legend()
    scan_runs = services["scan_repository"].list_runs(limit=50)
    if not scan_runs:
        st.info("No scan batches have been recorded yet.")
        return

    run_labels = {
        f"{_fmt(run.started_at)} · {run.status.value.replace('_', ' ').title()}": run
        for run in scan_runs
        if run.id is not None
    }
    default_label = st.session_state.get("history_selected_batch")
    if default_label not in run_labels:
        default_label = next(iter(run_labels))
    selected_label = st.selectbox(
        "Select batch",
        list(run_labels),
        index=list(run_labels).index(default_label),
        key="history_selected_batch",
    )
    run = run_labels[selected_label]

    recommendation_repo = services["recommendation_repository"]
    recommendation_batch = recommendation_repo.get_batch_for_scan_run(run.id or 0)
    all_recommendations = recommendation_repo.list_by_batch(recommendation_batch["id"]) if recommendation_batch else []
    recommendations = [item for item in all_recommendations if item.recommendation_type not in HIDDEN_RECOMMENDATION_TYPES]
    framework = services["framework_repository"].get(recommendation_batch["framework_version_id"]) if recommendation_batch else None

    summary_left, summary_middle, summary_right, summary_fourth = st.columns(4)
    summary_left.metric("Scan batch", _fmt(run.started_at))
    summary_middle.metric("Framework", framework.version if framework else "Unavailable")
    summary_right.metric("Recommendations", len(recommendations))
    summary_fourth.metric("Configured sources", len(run.sources_snapshot or ()))

    started = perf_counter()
    evidence = services["scan_repository"].list_evidence_for_run(run.id or 0)
    LOGGER.info("History batch %s: loaded %s evidence items in %.2fs", run.id, len(evidence), perf_counter() - started)

    export_started = perf_counter()
    source_lookup = {source.id: source for source in services["source_repository"].list_all() if source.id is not None}
    fallback_recoveries = services["fallback_recovery_repository"].list_for_scan_run(run.id or 0) if "fallback_recovery_repository" in services else []
    export_data = _serialise_batch(run, evidence, recommendation_batch, recommendations, framework, source_lookup, fallback_recoveries)
    LOGGER.info("History batch %s: serialised export in %.2fs", run.id, perf_counter() - export_started)
    st.download_button(
        "Download batch evidence (JSON)",
        data=export_data,
        file_name=f"batch_{run.id or 0}_evidence.json",
        mime="application/json",
    )

    st.subheader("Recommendations")
    if recommendation_batch:
        st.caption(f"Recommendation batch: {_fmt(recommendation_batch['created_at'])} · {len(recommendations)} recommendation(s)")
    if recommendations:
        recommendations_started = perf_counter()
        _render_recommendations(recommendations, evidence, source_lookup, run.id or 0)
        question_history = services["batch_question_repository"].list_by_batch(recommendation_batch["id"]) if recommendation_batch else []
        source_health = _source_health_rows(run, evidence, source_lookup)
        fallback_candidates = _source_fallback_candidates(run, evidence, source_lookup)
        source_maintenance = _combined_source_maintenance_recommendations(source_health, fallback_recoveries)
        recommendation_pack = _build_recommendation_pack(
            run.id,
            recommendation_batch,
            framework,
            evidence,
            recommendations,
            source_lookup,
            question_history,
            source_health,
            fallback_candidates,
            fallback_recoveries,
            source_maintenance,
        )
        pack_left, pack_right = st.columns(2)
        pack_left.download_button(
            "Download recommendation pack (JSON)",
            data=json.dumps(recommendation_pack, indent=2),
            file_name=f"recommendation_pack_batch_{run.id or 0}.json",
            mime="application/json",
        )
        pack_right.download_button(
            "Download recommendation pack (Markdown)",
            data=_recommendation_pack_markdown(recommendation_pack),
            file_name=f"recommendation_pack_batch_{run.id or 0}.md",
            mime="text/markdown",
        )
        if question_history:
            qa_summary = _question_history_summary(question_history)
            st.subheader("Ask AI conversation summary")
            qa_summary_left, qa_summary_middle, qa_summary_right = st.columns(3)
            qa_summary_left.metric("Questions", qa_summary["question_count"])
            qa_summary_middle.metric("First question", qa_summary["first_question_at"] or "Unknown")
            qa_summary_right.metric("Latest question", qa_summary["latest_question_at"] or "Unknown")
            st.caption(f"Common review themes: {', '.join(qa_summary['common_review_themes']) if qa_summary['common_review_themes'] else 'None detected yet'}")
            qa_left, qa_right = st.columns(2)
            qa_left.download_button(
                "Download Q&A history (CSV)",
                data=_question_history_csv(question_history),
                file_name=f"ask_ai_questions_batch_{run.id or 0}.csv",
                mime="text/csv",
            )
            qa_right.download_button(
                "Download Q&A history (Markdown)",
                data=_question_history_markdown(question_history, _fmt(recommendation_batch["created_at"])),
                file_name=f"ask_ai_questions_batch_{run.id or 0}.md",
                mime="text/markdown",
            )
        LOGGER.info("History batch %s: rendered recommendations in %.2fs", run.id, perf_counter() - recommendations_started)
    else:
        st.info("No recommendations have been generated for this batch yet.")

    st.subheader("Batch configuration")
    _render_batch_configuration(run, framework, recommendation_batch)

    if recommendation_batch and "source_url_recommendation_repository" in services:
        url_record = services["source_url_recommendation_repository"].get_for_batch(recommendation_batch["id"])
        if url_record:
            st.subheader("AI-suggested source URL replacements")
            st.caption("AI suggested URL — human review required. These suggestions do not change Source Configuration automatically.")
            try:
                url_payload = json.loads(url_record["raw_result"] or "{}")
                rows = []
                for source_item in url_payload.get("recommendations", []):
                    for suggestion in source_item.get("recommendations", []) if isinstance(source_item, dict) else []:
                        rows.append({
                            "Organisation": source_item.get("organisation", "Unknown"),
                            "Source": source_item.get("source_name", "Unknown"),
                            "Current URL": source_item.get("current_url", ""),
                            "Recommended URL": suggestion.get("url", ""),
                            "Reason": suggestion.get("reason", ""),
                            "Status": "AI suggested URL — human review required",
                        })
                st.dataframe(rows, hide_index=True, width="stretch")
            except (TypeError, json.JSONDecodeError):
                st.warning("Saved URL recommendation data could not be displayed; contact IT support.")

    st.subheader("Organised scan")
    filtered_evidence = _render_organised_scan(run, evidence, source_lookup)

    st.subheader("Scan report")
    render_started = perf_counter()
    _render_scan_report(
        run,
        filtered_evidence,
        services["source_repository"].list_all(),
        evidence,
        fallback_recoveries,
    )
    LOGGER.info("History batch %s: rendered scan report in %.2fs", run.id, perf_counter() - render_started)


def _render_organised_scan(run, evidence, source_lookup: dict) -> list:
    """Show the deterministic organisation-level map used for LLM recommendation generation."""
    st.caption(f"Evidence in selected batch: {len(evidence)}")
    filter_left, filter_middle, filter_right = st.columns(3)
    evidence_type_choice = filter_left.selectbox(
        "Filter evidence by type",
        _evidence_type_options(evidence),
        key=f"history_evidence_type_{run.id or 0}",
    )
    source_family_choice = filter_middle.selectbox(
        "Filter evidence by source family",
        _source_family_options(source_lookup),
        key=f"history_source_family_{run.id or 0}",
    )
    source_type_choice = filter_right.selectbox(
        "Filter evidence by source type",
        _source_type_options(source_lookup),
        key=f"history_source_type_{run.id or 0}",
    )
    filtered_evidence = evidence
    if evidence_type_choice != "All evidence types":
        filtered_evidence = [item for item in filtered_evidence if _evidence_type_label(item.evidence_type) == evidence_type_choice]
    if source_family_choice != "All source families":
        selected_family_key = source_family_choice.upper().replace(" ", "_")
        filtered_evidence = [
            item
            for item in filtered_evidence
            if source_lookup.get(item.source_id) and source_lookup[item.source_id].source_family.value == selected_family_key
        ]
    if source_type_choice != "All source types":
        selected_type_key = source_type_choice.upper().replace(" ", "_")
        filtered_evidence = [
            item
            for item in filtered_evidence
            if source_lookup.get(item.source_id) and source_lookup[item.source_id].source_type.value == selected_type_key
        ]
    if not filtered_evidence:
        st.info("No retained evidence is available to organise for this batch.")
        return filtered_evidence
    organised_scan = EvidenceOrganiser.build(filtered_evidence)
    export_scan = _enrich_organised_scan(organised_scan, filtered_evidence, source_lookup)
    quality = organised_scan.get("quality_summary", {})
    first, second, third, fourth = st.columns(4)
    first.metric("Evidence mix", quality.get("label", "Unknown"))
    second.metric("Primary evidence", quality.get("primary_evidence_items", 0))
    third.metric("Signal evidence", quality.get("signal_evidence_items", 0))
    fourth.metric("Organisations", organised_scan["organisation_count"])
    st.dataframe(_organised_scan_rows(organised_scan), hide_index=True, width="stretch")
    with st.expander("Review representative organised items by organisation", expanded=False):
        st.caption("Each bucket shows representative retained items from this batch, capped to keep the page responsive.")
        for organisation_payload in organised_scan.get("organisations", []):
            counts = organisation_payload.get("counts", {})
            total = sum(int(value or 0) for value in counts.values())
            if total == 0:
                continue
            with st.expander(f"{organisation_payload.get('organisation', 'Unknown organisation')} · {total} item(s)", expanded=False):
                for bucket, label in ORGANISED_SCAN_BUCKETS:
                    rows = _organised_scan_sample_rows(organisation_payload, bucket)
                    bucket_count = counts.get(bucket, 0)
                    if not rows and not bucket_count:
                        continue
                    st.markdown(f"**{label}** · showing {len(rows)} of {bucket_count}")
                    if rows:
                        st.dataframe(rows, hide_index=True, width="stretch")
                    else:
                        st.caption("No representative items retained for this bucket.")
    st.download_button(
        "Download organised scan (JSON)",
        data=json.dumps(export_scan, indent=2),
        file_name=f"batch_{run.id or 0}_organised_scan.json",
        mime="application/json",
    )
    return filtered_evidence


def _render_batch_configuration(run, framework, recommendation_batch) -> None:
    with st.expander("Configured sources used in this batch", expanded=False):
        sources = run.sources_snapshot or ()
        if not sources:
            st.info("No source snapshot was stored for this batch.")
        else:
            rows = []
            for source in sources:
                rows.append(
                    {
                        "Source type": _source_type_badge(str(source.get("source_type", ""))),
                        "Source role": _source_role_badge(str(source.get("source_role", ""))),
                        "LLM fallback allowed": "Yes" if source.get("llm_allowed", True) else "No",
                        "Organisation": source.get("organisation", "Unknown"),
                        "Source": source.get("name", "Unknown"),
                        "Country": source.get("country", "Unknown"),
                        "Evidence label": source.get("evidence_label", "Unknown"),
                        "Discovery URL": source.get("url", "Unknown"),
                        "Category": source.get("category", "Unknown"),
                        "Max articles": source.get("max_articles_per_scan", "Unknown"),
                        "Listing pages": source.get("max_listing_pages", "Unknown"),
                    }
                )
            st.dataframe(rows, hide_index=True, width="stretch")
    with st.expander("Framework used for comparison", expanded=False):
        if recommendation_batch is None:
            st.info("No framework version was linked to this batch.")
            return
        if framework is not None:
            st.write(f"Version: {framework.version}")
            st.write(f"Created: {_fmt(framework.created_at)}")
        else:
            st.info("No framework version was linked to this batch.")
        st.download_button(
            "Download framework workbook",
            data=_framework_xlsx_bytes(recommendation_batch["framework_snapshot"]),
            file_name=f"framework_batch_{run.id or 0}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def _render_scan_report(run, evidence, sources, full_batch_evidence=None, fallback_recoveries=None) -> None:
    first, second = st.columns([1, 3])
    first.metric("Evidence items", len(evidence))
    second.metric("Scan status", run.status.value.replace("_", " ").title())
    source_lookup = {source.id: source for source in sources if source.id is not None}
    if run.error_summary:
        st.warning(run.error_summary)
    health_rows = _source_health_rows(run, full_batch_evidence if full_batch_evidence is not None else evidence, source_lookup)
    if health_rows:
        st.subheader("Source health")
        st.caption("This checks every configured source in the selected batch, including sources that produced no retained evidence.")
        st.info(source_access_limits_note())
        health_counts = _source_health_status_counts(health_rows)
        health_left, health_middle_left, health_middle_right, health_right = st.columns(4)
        health_left.metric("Healthy sources", health_counts["Healthy"])
        health_middle_left.metric("Low evidence", health_counts["Low evidence"])
        health_middle_right.metric("No evidence", health_counts["No evidence"])
        health_right.metric("Errors", health_counts["Error"])
        health_status_choice = st.selectbox(
            "Filter source health by status",
            ["All statuses", "Error", "No evidence", "Low evidence", "Healthy"],
            key=f"source_health_status_{run.id or 0}",
        )
        visible_health_rows = _filter_source_health_rows(health_rows, health_status_choice)
        st.dataframe(visible_health_rows, hide_index=True, width="stretch")
        st.download_button(
            "Download source health (CSV)",
            data=_recommendation_summary_csv(visible_health_rows),
            file_name=f"source_health_batch_{run.id or 0}.csv",
            mime="text/csv",
        )
        fallback_candidates = _source_fallback_candidates(run, full_batch_evidence if full_batch_evidence is not None else evidence, source_lookup)
        if fallback_candidates:
            with st.expander("LLM fallback candidates", expanded=False):
                st.caption("Review/export view: these sources may be eligible for LLM-assisted recovery. Run Scan is the controlled page for executing a paid fallback recovery call.")
                readiness_counts = fallback_readiness_counts(fallback_candidates)
                ready_col, access_col, signal_col, manual_col = st.columns(4)
                ready_col.metric("Ready for prompt review", readiness_counts["Ready for prompt review"])
                access_col.metric("Needs access review", readiness_counts["Needs access review"])
                signal_col.metric("Optional signal recovery", readiness_counts["Optional signal recovery"])
                manual_col.metric("Manual review first", readiness_counts["Review manually first"] + readiness_counts["Needs source URL"])
                readiness_choice = st.selectbox(
                    "Filter fallback candidates by readiness",
                    FALLBACK_READINESS_FILTER_OPTIONS,
                    key=f"history_fallback_readiness_{run.id or 0}",
                )
                visible_fallback_candidates = filter_fallback_candidates(fallback_candidates, readiness_choice)
                st.dataframe(_badge_fallback_candidate_rows(visible_fallback_candidates), hide_index=True, width="stretch")
                st.download_button(
                    "Download fallback candidate plan (CSV)",
                    data=_recommendation_summary_csv(_badge_fallback_candidate_rows(visible_fallback_candidates)),
                    file_name=f"llm_fallback_candidates_batch_{run.id or 0}.csv",
                    mime="text/csv",
                )
                prompt_pack = [fallback_prompt_payload(row) for row in visible_fallback_candidates]
                prompt_left, prompt_right = st.columns(2)
                prompt_left.download_button(
                    "Download fallback request preview (JSON)",
                    data=json.dumps(prompt_pack, indent=2),
                    file_name=f"llm_fallback_request_preview_batch_{run.id or 0}.json",
                    mime="application/json",
                )
                prompt_right.download_button(
                    "Download fallback prompt preview (Markdown)",
                    data="\n\n---\n\n".join(fallback_prompt_markdown(row) for row in visible_fallback_candidates),
                    file_name=f"llm_fallback_prompt_preview_batch_{run.id or 0}.md",
                    mime="text/markdown",
                )
        source_maintenance = _combined_source_maintenance_recommendations(health_rows, fallback_recoveries)
        if source_maintenance:
            st.subheader("Unhealthy or unuseful sources — review and replace")
            st.caption("These configured links produced errors, no evidence, or low-value evidence. Review the reason and replace the URL manually through Source Configuration if needed.")
            maintenance_counts = source_maintenance_priority_counts(source_maintenance)
            high_col, medium_col, low_col = st.columns(3)
            high_col.metric("High priority", maintenance_counts["High"])
            medium_col.metric("Medium priority", maintenance_counts["Medium"])
            low_col.metric("Low priority", maintenance_counts["Low"])
            st.dataframe(source_maintenance, hide_index=True, width="stretch")
            st.download_button(
                "Download source maintenance recommendations (CSV)",
                data=_recommendation_summary_csv(source_maintenance),
                file_name=f"source_maintenance_recommendations_batch_{run.id or 0}.csv",
                mime="text/csv",
            )
    if not evidence:
        st.info("This scan did not store any evidence.")
        return
    grouped: dict[int, list] = defaultdict(list)
    for item in evidence:
        grouped[item.source_id].append(item)
    st.subheader("Batch evidence by source")
    summary_rows = []
    for source_id, items in grouped.items():
        source = source_lookup.get(source_id)
        summary_rows.append(
            {
                "Source type": _source_type_badge(source.source_type.value if source else ""),
                "Source role": _source_role_badge(source.source_role.value if source else ""),
                "Evidence type": _evidence_type_label(items[0].evidence_type if items else ""),
                "Organisation": source.organisation if source else "Unavailable",
                "Source": source.name if source else f"Source {source_id}",
                "Source label": source.evidence_label if source else "Unknown",
                "Country": source.country if source else "Unknown",
                "Evidence items": len(items),
            }
        )
    st.dataframe(sorted(summary_rows, key=lambda row: row["Evidence items"], reverse=True), hide_index=True, width="stretch")
    st.caption(f"Total evidence in this batch: {len(evidence)}")
    source_ids = list(grouped)
    source_labels = [
        f"{source_lookup.get(source_id).name if source_lookup.get(source_id) else f'Source {source_id}'} ({len(grouped[source_id])} article(s))"
        for source_id in source_ids
    ]
    selected_source_label = st.selectbox(
        "Select source to inspect",
        source_labels,
        key=f"history_source_select_{run.id or 0}",
    )
    selected_source_id = source_ids[source_labels.index(selected_source_label)]
    selected_items = grouped[selected_source_id]
    source = source_lookup.get(selected_source_id)
    st.caption(f"Discovery URL: {source.url if source else 'Unavailable'}")

    page_size = 10
    page_count = max(1, (len(selected_items) + page_size - 1) // page_size)
    st.caption("Evidence page number")
    if page_count > 1:
        page = st.number_input(
            "Evidence page number",
            min_value=1,
            max_value=page_count,
            value=1,
            step=1,
            label_visibility="collapsed",
            key=f"history_source_page_{run.id or 0}_{selected_source_id}",
        )
        st.caption(f"Showing {(int(page) - 1) * page_size + 1}-{min(int(page) * page_size, len(selected_items))} of {len(selected_items)} evidence item(s)")
    else:
        page = 1
        st.caption(f"Showing 1-{len(selected_items)} of {len(selected_items)} evidence item(s)")
    start = (int(page) - 1) * page_size
    end = start + page_size
    for item in selected_items[start:end]:
        with st.expander(f"Evidence {item.id} · {item.title}"):
            label = _credibility_label(item.evidence_type)
            st.caption(f"Evidence ID: {item.id}")
            st.caption(f"{item.organisation} · {_credibility_badge(label)} {label} · {_evidence_type_label(item.evidence_type)} · {item.publication_date or 'Publication date unavailable'}")
            st.write(f"Fetched at: {_fmt(item.extracted_at)}")
            st.link_button("Open source", item.url)
            st.write(_preview(item.article_text, 100))


def _render_recommendations(recommendations, evidence, source_lookup, batch_id: int = 0) -> None:
    evidence_by_id = {item.id: item for item in evidence if item.id is not None}
    counts = Counter(item.recommendation_type for item in recommendations)
    st.dataframe(
        [{"Recommendation type": _human_label(recommendation_type).title(), "Count": count} for recommendation_type, count in counts.most_common()],
        hide_index=True,
        width="stretch",
    )
    family_rows, organisation_rows = _support_coverage_rows(recommendations, evidence_by_id, source_lookup)
    if family_rows or organisation_rows:
        st.subheader("Support coverage")
        coverage_left, coverage_right = st.columns(2)
        coverage_left.caption("Cited evidence by source family")
        coverage_left.dataframe(family_rows, hide_index=True, width="stretch")
        coverage_left.download_button(
            "Download source family coverage (CSV)",
            data=_recommendation_summary_csv(family_rows),
            file_name=f"support_coverage_source_family_batch_{batch_id}.csv",
            mime="text/csv",
        )
        coverage_right.caption("Top cited organisations")
        coverage_right.dataframe(organisation_rows[:10], hide_index=True, width="stretch")
        coverage_right.download_button(
            "Download organisation coverage (CSV)",
            data=_recommendation_summary_csv(organisation_rows),
            file_name=f"support_coverage_organisations_batch_{batch_id}.csv",
            mime="text/csv",
        )
    st.subheader("Recommendation summary")
    st.caption("Use this table to triage recommendations before opening the detailed evidence cards.")
    summary_rows = _recommendation_summary_rows(recommendations, evidence_by_id, source_lookup)
    st.dataframe(
        summary_rows,
        hide_index=True,
        width="stretch",
    )
    st.download_button(
        "Download recommendation summary (CSV)",
        data=_recommendation_summary_csv(summary_rows),
        file_name=f"recommendation_summary_batch_{batch_id}.csv",
        mime="text/csv",
    )
    for recommendation in recommendations:
        support_summary = _support_summary(recommendation, evidence_by_id, source_lookup)
        with st.expander(f"{_human_label(recommendation.recommendation_type).title()} · {recommendation.confidence:.0%} confidence · {support_summary}"):
            st.caption(f"Support strength: {support_summary}")
            st.markdown("**Sub functional area**")
            st.write(recommendation.sub_functional_area or "Not specified")
            st.markdown("**Competency**")
            st.write(recommendation.competency or "Not specified")
            st.markdown("**Kind of changes suggested**")
            st.write(recommendation.kind_of_changes_suggested or _human_label(recommendation.recommendation_type).title())
            st.markdown("**Reasons for suggesting the changes**")
            st.write(recommendation.reasons_for_suggesting_the_changes or recommendation.reasoning)
            st.markdown("**Sources supporting the reasons**")
            if recommendation.supporting_evidence_ids:
                for index, evidence_id in enumerate(recommendation.supporting_evidence_ids):
                    evidence_item = evidence_by_id.get(evidence_id)
                    if evidence_item:
                        source_label = _source_label(evidence_item.evidence_type)
                        badge = _credibility_badge(source_label)
                        country = getattr(evidence_item, "country", "Unknown") or "Unknown"
                        source = source_lookup.get(evidence_item.source_id)
                        type_badge = _source_type_badge(source.source_type.value if source else "")
                        role_badge = _source_role_badge(source.source_role.value if source else "")
                        with st.expander(f"Evidence {evidence_item.id} · {badge} {source_label} · {type_badge} · {role_badge} · {evidence_item.title} · {evidence_item.organisation} · {country}"):
                            st.caption(f"Evidence ID: {evidence_item.id}")
                            st.caption(
                                f"{evidence_item.organisation} · {badge} {source_label} · {_evidence_type_label(evidence_item.evidence_type)} · {type_badge} · {role_badge} · {country}"
                            )
                            st.caption(f"Published: {evidence_item.publication_date or 'Unavailable'}")
                            st.caption(f"Evidence state: {evidence_item.explicit_or_inferred}")
                            st.markdown(f"[Open supporting source]({evidence_item.url})")
                            st.write(_preview(evidence_item.article_text, 100))
                    else:
                        fallback_url = recommendation.supporting_urls[index] if index < len(recommendation.supporting_urls) else None
                        fallback_org = recommendation.supporting_organisations[index] if index < len(recommendation.supporting_organisations) else "Source"
                        fallback_source = _source_from_organisation(fallback_org, source_lookup)
                        family_badge = _source_family_badge(fallback_source.source_family.value if fallback_source else "")
                        type_badge = _source_type_badge(fallback_source.source_type.value if fallback_source else "")
                        role_badge = _source_role_badge(fallback_source.source_role.value if fallback_source else "")
                        if fallback_url:
                            st.markdown(f"- {family_badge} · {type_badge} · {role_badge} · {fallback_org}: [{fallback_url}]({fallback_url})")
                        else:
                            st.caption(f"Evidence ID {evidence_id} is no longer retained as full evidence text.")
            elif recommendation.supporting_urls:
                for url in recommendation.supporting_urls:
                    st.markdown(f"- {url}")
            else:
                st.info("No supporting sources were recorded for this recommendation.")


def _support_summary(recommendation, evidence_by_id: dict, source_lookup: dict) -> str:
    """Return compact support strength text for one recommendation."""
    evidence_items = [evidence_by_id.get(evidence_id) for evidence_id in recommendation.supporting_evidence_ids]
    evidence_items = [item for item in evidence_items if item is not None]
    organisations = {item.organisation for item in evidence_items if item.organisation}
    families = {
        source_lookup[item.source_id].source_family.value
        for item in evidence_items
        if item.source_id in source_lookup
    }
    if not evidence_items:
        source_count = len({url for url in recommendation.supporting_urls if url}) or len(set(recommendation.supporting_evidence_ids))
        organisation_count = len({org for org in recommendation.supporting_organisations if org})
        families = _source_families_from_organisations(recommendation.supporting_organisations, source_lookup)
        if source_count:
            family_text = f"{len(families)} source family type(s)" if families else "source family unavailable"
            return f"{source_count} source(s) · {organisation_count} org(s) · {family_text}"
        return "0 sources"
    return f"{len(evidence_items)} source(s) · {len(organisations)} org(s) · {len(families)} source family type(s)"


def _support_metrics(recommendation, evidence_by_id: dict, source_lookup: dict) -> dict:
    """Return support counts for summary table sorting and review."""
    evidence_items = [evidence_by_id.get(evidence_id) for evidence_id in recommendation.supporting_evidence_ids]
    evidence_items = [item for item in evidence_items if item is not None]
    organisations = {item.organisation for item in evidence_items if item.organisation}
    families = {
        source_lookup[item.source_id].source_family.value
        for item in evidence_items
        if item.source_id in source_lookup
    }
    if not evidence_items:
        source_count = len({url for url in recommendation.supporting_urls if url}) or len(set(recommendation.supporting_evidence_ids))
        organisation_count = len({org for org in recommendation.supporting_organisations if org})
        families = _source_families_from_organisations(recommendation.supporting_organisations, source_lookup)
        return {
            "Supporting sources": source_count,
            "Supporting organisations": organisation_count,
            "Source family types": len(families) if families else ("Unavailable" if source_count else 0),
        }
    return {
        "Supporting sources": len(evidence_items),
        "Supporting organisations": len(organisations),
        "Source family types": len(families),
    }


def _source_families_from_organisations(organisations: tuple[str, ...], source_lookup: dict) -> set[str]:
    """Infer source-family coverage from stored supporting organisation names."""
    configured_by_organisation = {
        source.organisation.strip().casefold(): source.source_family.value
        for source in source_lookup.values()
        if source.organisation
    }
    return {
        configured_by_organisation[organisation.strip().casefold()]
        for organisation in organisations
        if organisation and organisation.strip().casefold() in configured_by_organisation
    }


def _source_from_organisation(organisation: str, source_lookup: dict):
    """Return a configured source with the same organisation name, if available."""
    organisation_key = (organisation or "").strip().casefold()
    for source in source_lookup.values():
        if source.organisation and source.organisation.strip().casefold() == organisation_key:
            return source
    return None


def _recommendation_summary_rows(recommendations, evidence_by_id: dict, source_lookup: dict) -> list[dict]:
    """Return officer-facing recommendation summary rows."""
    rows = []
    for index, recommendation in enumerate(recommendations, start=1):
        row = {
            "#": index,
            "Type": recommendation.recommendation_type.replace("_", " ").title(),
            "Confidence": f"{recommendation.confidence:.0%}",
            "Sub functional area": recommendation.sub_functional_area or "Not specified",
            "Competency": recommendation.competency or "Not specified",
        }
        row.update(_support_metrics(recommendation, evidence_by_id, source_lookup))
        rows.append(row)
    return rows


def _serialise_batch(run, evidence, recommendation_batch, recommendations, framework, source_lookup, fallback_recoveries: list | None = None) -> str:
    source_health = _source_health_rows(run, evidence, source_lookup)
    fallback_candidates = _source_fallback_candidates(run, evidence, source_lookup)
    source_maintenance = _combined_source_maintenance_recommendations(source_health, fallback_recoveries)
    payload = {
        "scan_run": {
            "id": run.id,
            "started_at": _fmt(run.started_at),
            "completed_at": _fmt(run.completed_at) if run.completed_at else None,
            "status": run.status.value,
            "error_summary": run.error_summary,
            "sources_snapshot": list(run.sources_snapshot or ()),
        },
        "source_health": source_health,
        "source_health_counts": _source_health_status_counts(source_health),
        "source_maintenance_recommendations": source_maintenance,
        "source_maintenance_priority_counts": source_maintenance_priority_counts(source_maintenance),
        "llm_fallback_candidates": fallback_candidates,
        "llm_fallback_readiness_counts": fallback_readiness_counts(fallback_candidates),
        "llm_fallback_request_preview": [fallback_prompt_payload(row) for row in fallback_candidates],
        "llm_fallback_recoveries": _fallback_recovery_payloads(fallback_recoveries),
        "framework": (
            {
                "version": framework.version,
                "created_at": _fmt(framework.created_at),
            }
            if framework
            else None
        ),
        "recommendation_batch": (
            {
                "id": recommendation_batch["id"],
                "created_at": _fmt(recommendation_batch["created_at"]),
                "recommendation_count": len(recommendations),
            }
            if recommendation_batch
            else None
        ),
        "evidence": [
            {
                "id": item.id,
                "source_id": item.source_id,
                "title": item.title,
                "publication_date": item.publication_date,
                "organisation": item.organisation,
                "country": source_lookup.get(item.source_id).country if source_lookup.get(item.source_id) else "Unknown",
                "evidence_type": item.evidence_type,
                "source_label": _source_label(item.evidence_type),
                "explicit_or_inferred": item.explicit_or_inferred,
                "url": item.url,
                "article_text": item.article_text,
                "extracted_at": _fmt(item.extracted_at),
            }
            for item in evidence
        ],
        "recommendations": [
            {
                "id": recommendation.id,
                "batch_id": recommendation.batch_id,
                "recommendation_type": recommendation.recommendation_type,
                "confidence": recommendation.confidence,
                "reasoning": recommendation.reasoning,
                "sub_functional_area": recommendation.sub_functional_area,
                "competency": recommendation.competency,
                "kind_of_changes_suggested": recommendation.kind_of_changes_suggested,
                "reasons_for_suggesting_the_changes": recommendation.reasons_for_suggesting_the_changes,
                "supporting_evidence_ids": list(recommendation.supporting_evidence_ids),
                "supporting_urls": list(recommendation.supporting_urls),
                "supporting_organisations": list(recommendation.supporting_organisations),
                "supporting_evidence": _evidence_reference_payload(recommendation, {item.id: item for item in evidence if item.id is not None}),
            }
            for recommendation in recommendations
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
