"""Recommendation generation page."""
from collections import Counter
import csv
import json
from datetime import datetime
from io import StringIO
import streamlit as st
from src.core.exceptions import RecommendationError
from src.services.evidence_organiser import EvidenceOrganiser
from src.services.fallback_provenance import fallback_provenance_label, fallback_verification_label
from src.services.fallback_verification_workflow import verify_recovery_record
from src.services.source_health_service import FALLBACK_READINESS_FILTER_OPTIONS, combined_source_maintenance_recommendations, filter_fallback_candidates, filter_source_health_rows, fallback_prompt_markdown, fallback_prompt_payload, fallback_readiness_counts, replacement_url_prompt_markdown, source_access_limits_note, source_fallback_candidates, source_health_action, source_health_rows, source_health_status_counts, source_maintenance_priority_counts, source_maintenance_recommendations

HIDDEN_RECOMMENDATION_TYPES = {"ALREADY_COVERED", "INSUFFICIENT_EVIDENCE"}
ASK_AI_EVIDENCE_PREVIEW_CHARS = 1200
ASK_AI_RECENT_QA_LIMIT = 10
ASK_AI_QUESTION_STARTERS = [
    "Which recommendation is most supported by professional bodies or official guidance?",
    "Which recommendations rely mostly on trend/news signals and should be treated more cautiously?",
    "Why is Recommendation 1 suggested?",
    "Which recommendations suggest genuinely new STE sub-functional areas not covered by the current framework?",
    "Which outlier signal is the strongest and why?",
]


def _fmt(dt_value) -> str:
    if isinstance(dt_value, str):
        dt_value = datetime.fromisoformat(dt_value[:19].replace("T", " "))
    return dt_value.strftime("%Y-%m-%d %H:%M") if dt_value else "Unknown"


def _visible_count(batch_id: int, repository) -> int:
    return sum(
        1
        for item in repository.list_by_batch(batch_id)
        if item.recommendation_type not in HIDDEN_RECOMMENDATION_TYPES
    )


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


def _source_health_action(status: str, llm_allowed: bool) -> str:
    """Return a plain-language action suggestion for one source-health status."""
    return source_health_action(status, llm_allowed)


def _current_source_health_rows(run, evidence: list, source_lookup: dict) -> list[dict]:
    """Build source-health rows for the current recommendation batch export."""
    rows = source_health_rows(run, evidence, source_lookup)
    for row in rows:
        row["Source family"] = _source_family_badge(str(row.get("Source family", "")))
        row["Source type"] = _source_type_badge(str(row.get("Source type", "")))
        row["Source role"] = _source_role_badge(str(row.get("Source role", "")))
    return rows


def _current_fallback_candidates(run, evidence: list, source_lookup: dict) -> list[dict]:
    """Build raw fallback candidate rows for Ask AI and exports."""
    return source_fallback_candidates(run, evidence, source_lookup)


def _current_source_maintenance_recommendations(source_health: list[dict]) -> list[dict]:
    """Build deterministic source-link maintenance recommendations."""
    return source_maintenance_recommendations(source_health)


def _current_combined_source_maintenance_recommendations(source_health: list[dict], fallback_recoveries: list | None = None) -> list[dict]:
    """Build deterministic plus LLM-assisted source-link maintenance recommendations."""
    return combined_source_maintenance_recommendations(source_health, fallback_recoveries)


def _fallback_recovery_payloads(recoveries: list | None) -> list[dict]:
    """Return JSON-safe saved fallback recovery records for Ask AI and exports."""
    payloads = []
    for recovery in recoveries or []:
        try:
            raw_result = json.loads(getattr(recovery, "raw_result", "{}") or "{}")
        except json.JSONDecodeError:
            raw_result = {"raw_result": getattr(recovery, "raw_result", "")}
        payloads.append(
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
                "created_at": _fmt(recovery.created_at),
                "result": raw_result,
            }
        )
    return payloads


def _badge_fallback_candidate_rows(rows: list[dict]) -> list[dict]:
    """Return fallback candidates with dashboard badges for display."""
    display_rows = []
    for row in rows:
        display_row = dict(row)
        display_row["Source family"] = _source_family_badge(str(row.get("Source family", "")))
        display_row["Source type"] = _source_type_badge(str(row.get("Source type", "")))
        display_row["Source role"] = _source_role_badge(str(row.get("Source role", "")))
        display_rows.append(display_row)
    return display_rows


def _fallback_recovery_summary_rows(recoveries: list | None) -> list[dict]:
    """Return compact rows for saved fallback recoveries in the current batch UI."""
    rows = []
    for recovery in recoveries or []:
        try:
            raw_result = json.loads(getattr(recovery, "raw_result", "{}") or "{}")
        except json.JSONDecodeError:
            raw_result = {}
        rows.append(
            {
                "Record ID": recovery.id,
                "Created": _fmt(recovery.created_at),
                "Status": recovery.recovery_status.replace("_", " ").title(),
                "Provenance": fallback_provenance_label(),
                "Verification": raw_result.get("verification_summary") or fallback_verification_label(),
                "Organisation": recovery.organisation,
                "Source": recovery.source_name,
                "Recovered items": recovery.recovered_item_count,
                "Source advice": _source_maintenance_advice_summary(raw_result.get("source_maintenance_advice", {})),
                "Source URL": recovery.source_url,
            }
        )
    return rows


def _source_maintenance_advice_summary(advice: dict) -> str:
    """Return compact source-maintenance advice text from fallback recovery output."""
    if not isinstance(advice, dict) or not advice:
        return "No advice recorded"
    advice_type = str(advice.get("recommendation_type", "NO_CLEAR_ADVICE")).replace("_", " ").title().replace("Url", "URL").replace("It", "IT").replace("Pdf", "PDF")
    confidence = advice.get("confidence")
    confidence_text = f" · {float(confidence):.0%}" if isinstance(confidence, (float, int)) else ""
    reason = str(advice.get("reason", "")).strip()
    reason_text = f" · Reason: {reason}" if reason else ""
    urls = advice.get("recommended_replacement_urls") or []
    url_text = f" · Suggested URL(s): {', '.join(urls)}" if urls else ""
    return f"{advice_type}{confidence_text}{reason_text}{url_text}"


def _source_family_badge(source_family: str) -> str:
    value = (source_family or "").upper()
    if value == "PROFESSIONAL_BODY":
        return "🟢 professional body"
    if value == "HIGHER_LEARNING":
        return "🔵 higher learning"
    if value == "GOVERNMENT_AGENCY":
        return "🟣 government agency"
    return "⚪ source family"


def _show_credibility_legend() -> None:
    st.info(
        "Credibility guide: 🟢 standards / reports are strongest; 🔵 official guidance / research is strong; "
        "🟠 news / commentary is moderate; ⚪ catalogue / training is softer."
    )


def _source_family_options(source_lookup: dict) -> list[str]:
    values = sorted({source.source_family.value.replace("_", " ").title() for source in source_lookup.values()})
    return ["All source families"] + values


def _source_type_options(source_lookup: dict) -> list[str]:
    values = sorted({source.source_type.value.replace("_", " ").title() for source in source_lookup.values()})
    return ["All source types"] + values


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


def _support_coverage_rows(recommendations, evidence_by_id: dict, source_lookup: dict) -> tuple[list[dict], list[dict]]:
    """Return source-family and organisation citation coverage for visible recommendations."""
    family_counts: Counter[str] = Counter()
    organisation_counts: Counter[str] = Counter()
    for recommendation in recommendations:
        evidence_items = [evidence_by_id.get(evidence_id) for evidence_id in recommendation.supporting_evidence_ids]
        evidence_items = [item for item in evidence_items if item is not None]
        if evidence_items:
            for item in evidence_items:
                organisation_counts[item.organisation or "Unknown"] += 1
                source = source_lookup.get(item.source_id)
                family_counts[_human_label(source.source_family.value).title() if source else "Unknown"] += 1
            continue
        for organisation in recommendation.supporting_organisations:
            organisation_counts[organisation or "Unknown"] += 1
        for family in _source_families_from_organisations(recommendation.supporting_organisations, source_lookup):
            family_counts[_human_label(family).title()] += 1
    family_rows = [{"Source family": family, "Cited evidence count": count} for family, count in family_counts.most_common()]
    organisation_rows = [{"Organisation": organisation, "Cited evidence count": count} for organisation, count in organisation_counts.most_common()]
    return family_rows, organisation_rows


def _source_health_status_counts(rows: list[dict]) -> dict[str, int]:
    """Count source-health statuses for recommendation-pack exports."""
    return source_health_status_counts(rows)


def _filter_source_health_rows(rows: list[dict], status_choice: str) -> list[dict]:
    """Filter source-health rows by status while preserving the full default view."""
    return filter_source_health_rows(rows, status_choice)


def _recommendation_summary_csv(rows: list[dict]) -> str:
    """Return recommendation summary rows as CSV for spreadsheet review."""
    if not rows:
        return ""
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _question_history_csv(question_history) -> str:
    """Return saved Ask AI questions as CSV text."""
    rows = [
        {
            "Asked at": _fmt(row["asked_at"]),
            "Question": row["question"],
            "Answer": row["answer"],
        }
        for row in question_history
    ]
    if not rows:
        return ""
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _markdown_text(value) -> str:
    """Return a single-line Markdown-safe text value for table cells and labels."""
    return str(value if value is not None else "").replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def _human_label(value) -> str:
    """Convert enum-like values into compact human-readable labels."""
    return _markdown_text(value).replace("_", " ").lower()


def _text_preview(text: str, max_chars: int = ASK_AI_EVIDENCE_PREVIEW_CHARS) -> str:
    """Return a compact whitespace-normalised preview for LLM context."""
    compact = " ".join((text or "").split())
    return compact[:max_chars]


def _preview_payload(text: str, max_chars: int = ASK_AI_EVIDENCE_PREVIEW_CHARS) -> dict:
    """Return preview text plus transparency metadata for LLM context."""
    compact = " ".join((text or "").split())
    preview = compact[:max_chars]
    return {
        "article_preview": preview,
        "article_preview_chars": len(preview),
        "article_original_chars": len(compact),
        "article_preview_truncated": len(compact) > max_chars,
    }


def _framework_payload(framework, selected_batch) -> dict:
    """Return a JSON-safe framework context for Ask AI."""
    snapshot = {}
    if selected_batch is not None and "framework_snapshot" in selected_batch.keys():
        try:
            snapshot = json.loads(selected_batch["framework_snapshot"] or "{}")
        except json.JSONDecodeError:
            snapshot = {"raw_snapshot": selected_batch["framework_snapshot"]}
    if isinstance(framework, dict):
        return {"metadata": framework, "snapshot": snapshot}
    if framework is None:
        return {"metadata": {}, "snapshot": snapshot}
    return {
        "metadata": {
            "id": framework.id,
            "version": framework.version,
            "created_at": _fmt(framework.created_at),
            "is_current": framework.is_current,
        },
        "snapshot": snapshot,
    }


def _recent_question_history(question_history, limit: int = ASK_AI_RECENT_QA_LIMIT) -> list[dict]:
    """Return a bounded recent Ask AI transcript for batch-local conversation context."""
    rows = list(question_history or [])[:limit]
    return [
        {
            "id": row["id"],
            "asked_at": _fmt(row["asked_at"]),
            "question": row["question"],
            "answer": _text_preview(row["answer"], 1000),
            "answer_preview_truncated": len(" ".join((row["answer"] or "").split())) > 1000,
        }
        for row in rows
    ]


def _question_history_summary(question_history) -> dict:
    """Return a compact deterministic summary of saved same-batch Ask AI discussion."""
    rows = list(question_history or [])
    if not rows:
        return {
            "question_count": 0,
            "first_question_at": None,
            "latest_question_at": None,
            "common_review_themes": [],
            "recent_questions": [],
        }
    chronological = sorted(rows, key=lambda row: str(row["asked_at"]))
    themes = _question_history_themes(rows)
    return {
        "question_count": len(rows),
        "first_question_at": _fmt(chronological[0]["asked_at"]),
        "latest_question_at": _fmt(chronological[-1]["asked_at"]),
        "common_review_themes": themes,
        "recent_questions": [
            {
                "asked_at": _fmt(row["asked_at"]),
                "question": _text_preview(row["question"], 220),
            }
            for row in rows[:5]
        ],
    }


def _question_history_themes(question_history) -> list[str]:
    """Classify Ask AI questions into lightweight review themes."""
    theme_markers = {
        "Evidence strength": ("evidence", "support", "source", "legitimacy", "credible", "strongest", "weak"),
        "Recommendation prioritisation": ("priority", "prioritise", "review first", "important", "broadest"),
        "Outlier or trend signals": ("outlier", "trend", "signal", "emerging", "new combination"),
        "Source health or fallback": ("fallback", "crawler", "source health", "blocked", "access", "url"),
        "Framework comparison": ("framework", "covered", "gap", "existing", "competency", "sub-functional"),
    }
    counts: Counter[str] = Counter()
    for row in question_history or []:
        text = f"{row['question']} {row['answer']}".casefold()
        for theme, markers in theme_markers.items():
            if any(marker in text for marker in markers):
                counts[theme] += 1
    return [theme for theme, _ in counts.most_common()]


def _build_question_context(selected_run_id, selected_batch, framework, evidence, recommendations, source_lookup: dict, source_health: list[dict] | None = None, fallback_candidates: list[dict] | None = None, fallback_recoveries: list | None = None, question_history=None, source_maintenance: list[dict] | None = None) -> dict:
    """Build the auditable context supplied to the batch question-answering LLM."""
    total_evidence = len(evidence)
    cited_ids = {eid for item in recommendations for eid in item.supporting_evidence_ids}
    cited_urls = {url for item in recommendations for url in item.supporting_urls if url}
    evidence = [item for item in evidence if item.id in cited_ids or item.url in cited_urls]
    evidence_by_id = {item.id: item for item in evidence if item.id is not None}
    recommendation_summary = _recommendation_summary_rows(recommendations, evidence_by_id, source_lookup)
    family_rows, organisation_rows = _support_coverage_rows(recommendations, evidence_by_id, source_lookup)
    organised_scan_quality = EvidenceOrganiser.build(evidence).get("quality_summary", {})
    evidence_payload = [
        {
            "id": item.id,
            "title": item.title,
            "organisation": item.organisation,
            "url": item.url,
            "evidence_type": item.evidence_type,
            "explicit_or_inferred": item.explicit_or_inferred,
            "source_id": item.source_id,
            **_preview_payload(item.article_text),
        }
        for item in evidence
    ]
    recommendations_payload = [
        {
            "id": item.id,
            "recommendation_type": item.recommendation_type,
            "confidence": item.confidence,
            "reasoning": item.reasoning,
            "sub_functional_area": item.sub_functional_area,
            "competency": item.competency,
            "kind_of_changes_suggested": item.kind_of_changes_suggested,
            "reasons_for_suggesting_the_changes": item.reasons_for_suggesting_the_changes,
            "supporting_evidence_ids": list(item.supporting_evidence_ids),
            "supporting_urls": list(item.supporting_urls),
            "supporting_organisations": list(item.supporting_organisations),
            "support_profile": _support_metrics(item, evidence_by_id, source_lookup),
            "support_summary": _support_summary(item, evidence_by_id, source_lookup),
        }
        for item in recommendations
    ]
    maintenance_rows = source_maintenance if source_maintenance is not None else _current_combined_source_maintenance_recommendations(source_health or [], fallback_recoveries)
    return {
        "scan_batch": {"id": selected_run_id, "label": _fmt(selected_batch["created_at"]) if selected_batch else "Unknown"},
        # Never forward arbitrary batch columns: snapshots can contain the whole scan.
        "recommendation_batch": {key: selected_batch[key] for key in
            ("id", "scan_run_id", "created_at", "framework_version_id", "recommendation_count")
            if selected_batch is not None and key in selected_batch.keys()},
        "evidence_scope": {"scope": "recommendation-cited evidence only",
                           "retained_batch_items": total_evidence,
                           "included_items": len(evidence),
                           "missing_cited_ids": sorted(cited_ids - set(evidence_by_id))},
        "framework": _framework_payload(framework, selected_batch),
        "recommendation_summary": recommendation_summary,
        "support_coverage": {
            "source_families": family_rows,
            "organisations": organisation_rows,
        },
        "organised_scan_quality": organised_scan_quality,
        "source_health": source_health or [],
        "source_health_counts": _source_health_status_counts(source_health or []),
        "source_maintenance_recommendations": maintenance_rows,
        "source_maintenance_priority_counts": source_maintenance_priority_counts(maintenance_rows),
        "llm_fallback_candidates": fallback_candidates or [],
        "llm_fallback_readiness_counts": fallback_readiness_counts(fallback_candidates or []),
        "llm_fallback_request_preview": [fallback_prompt_payload(row) for row in (fallback_candidates or [])],
        "llm_fallback_recoveries": _fallback_recovery_payloads(fallback_recoveries),
        "question_history_summary": _question_history_summary(question_history),
        "recent_question_history": _recent_question_history(question_history),
        "question_history_policy": {
            "scope": "same recommendation batch only",
            "recent_turn_limit": ASK_AI_RECENT_QA_LIMIT,
            "use_as": "conversation context only, not source evidence",
        },
        "evidence": evidence_payload,
        "recommendations": recommendations_payload,
        "source_lookup": {
            source_id: {
                "name": source.name,
                "organisation": source.organisation,
                "country": source.country,
                "source_family": source.source_family.value,
                "source_type": source.source_type.value,
                "source_role": source.source_role.value,
            }
            for source_id, source in source_lookup.items()
            if source_id in {item.source_id for item in evidence}
        },
    }


def _compact_live_question_context(context: dict) -> dict:
    """Keep detailed diagnostics in exports, not in the live recommendation Q&A."""
    compact = dict(context)
    for key in ('source_health', 'source_maintenance_recommendations',
                'llm_fallback_candidates', 'llm_fallback_readiness_counts',
                'llm_fallback_request_preview', 'llm_fallback_recoveries'):
        compact.pop(key, None)
    compact['diagnostic_scope'] = 'Summary counts only; per-source diagnostics are available in the app, not this context.'
    return compact


def _build_recommendation_pack(selected_run_id, selected_batch, framework, evidence, recommendations, source_lookup: dict, question_history, source_health: list[dict] | None = None, fallback_candidates: list[dict] | None = None, fallback_recoveries: list | None = None, source_maintenance: list[dict] | None = None) -> dict:
    """Build a compact downloadable recommendation pack for supervisor review."""
    context = _build_question_context(selected_run_id, selected_batch, framework, evidence, recommendations, source_lookup, source_health, fallback_candidates, fallback_recoveries, question_history, source_maintenance)
    evidence_lookup = {item.id: item for item in evidence if item.id is not None}
    cited_evidence_ids = sorted({evidence_id for recommendation in recommendations for evidence_id in recommendation.supporting_evidence_ids})
    cited_evidence = [
        {
            "id": item.id,
            "title": item.title,
            "organisation": item.organisation,
            "url": item.url,
            "evidence_type": item.evidence_type,
            "explicit_or_inferred": item.explicit_or_inferred,
            "source_id": item.source_id,
        }
        for evidence_id in cited_evidence_ids
        if (item := evidence_lookup.get(evidence_id)) is not None
    ]
    source_lookup_payload = context["source_lookup"]
    for recommendation in context["recommendations"]:
        recommendation["supporting_sources"] = _supporting_source_payload(
            recommendation.get("supporting_organisations", ()),
            recommendation.get("supporting_urls", ()),
            source_lookup_payload,
            recommendation.get("supporting_evidence_ids", ()),
            evidence_lookup,
        )
    return {
        "export_type": "recommendation_pack",
        "generated_at": _fmt(datetime.now().astimezone()),
        "scan_batch": context["scan_batch"],
        "recommendation_batch": context["recommendation_batch"],
        "framework": context["framework"],
        "recommendation_summary": context["recommendation_summary"],
        "support_coverage": context["support_coverage"],
        "organised_scan_quality": context["organised_scan_quality"],
        "source_health": context["source_health"],
        "source_health_counts": context["source_health_counts"],
        "source_maintenance_recommendations": context["source_maintenance_recommendations"],
        "source_maintenance_priority_counts": context["source_maintenance_priority_counts"],
        "llm_fallback_candidates": context["llm_fallback_candidates"],
        "llm_fallback_readiness_counts": context["llm_fallback_readiness_counts"],
        "llm_fallback_request_preview": context["llm_fallback_request_preview"],
        "llm_fallback_recoveries": context["llm_fallback_recoveries"],
        "question_history_summary": context["question_history_summary"],
        "recommendations": context["recommendations"],
        "cited_evidence": cited_evidence,
        "source_lookup": source_lookup_payload,
        "saved_questions": [
            {
                "id": row["id"],
                "asked_at": _fmt(row["asked_at"]),
                "question": row["question"],
                "answer": row["answer"],
            }
            for row in question_history
        ],
    }


def _supporting_source_payload(organisations, urls, source_lookup_payload: dict, evidence_ids=(), evidence_lookup: dict | None = None) -> list[dict]:
    """Pair supporting organisations and URLs with source metadata for export."""
    evidence_lookup = evidence_lookup or {}
    sources_by_organisation = {
        source.get("organisation", "").strip().casefold(): source
        for source in source_lookup_payload.values()
        if source.get("organisation")
    }
    rows = []
    organisations = tuple(organisations or ())
    urls = tuple(urls or ())
    evidence_ids = tuple(evidence_ids or ())
    max_len = max(len(organisations), len(urls), len(evidence_ids))
    for index in range(max_len):
        organisation = organisations[index] if index < len(organisations) else "Source"
        url = urls[index] if index < len(urls) else ""
        evidence_id = evidence_ids[index] if index < len(evidence_ids) else None
        evidence_item = evidence_lookup.get(evidence_id)
        source = sources_by_organisation.get(str(organisation).strip().casefold(), {})
        rows.append(
            {
                "evidence_id": evidence_id,
                "title": evidence_item.title if evidence_item else "",
                "evidence_type": evidence_item.evidence_type if evidence_item else "Unknown",
                "organisation": organisation,
                "url": url,
                "country": source.get("country", "Unknown"),
                "source_family": source.get("source_family", "Unknown"),
                "source_type": source.get("source_type", "Unknown"),
                "source_role": source.get("source_role", "Unknown"),
            }
        )
    return rows


def _recommendation_pack_markdown(pack: dict) -> str:
    """Render a compact human-readable recommendation pack."""
    lines = [
        "# Recommendation Pack",
        "",
        f"Generated at: {pack.get('generated_at', 'Unknown')}",
        f"Scan batch: {pack.get('scan_batch', {}).get('label', 'Unknown')}",
        f"Framework: {pack.get('framework', {}).get('metadata', {}).get('version', 'Unavailable')}",
        "",
    ]
    quality = pack.get("organised_scan_quality", {})
    if quality:
        lines.extend(
            [
                "## Organised scan quality",
                "",
                f"Evidence mix: {_markdown_text(quality.get('label', 'Unknown'))} · Primary evidence: {_markdown_text(quality.get('primary_evidence_items', 0))} · Signal evidence: {_markdown_text(quality.get('signal_evidence_items', 0))} · Primary share: {_markdown_text(quality.get('primary_share', 0))}",
                "",
            ]
        )
    lines.extend(
        [
            "## Recommendation summary",
            "",
            "| # | Type | Confidence | Sub functional area | Competency | Sources | Organisations | Source family types |",
            "| - | ---- | ---------- | ------------------- | ---------- | ------- | ------------- | ------------------- |",
        ]
    )
    for row in pack.get("recommendation_summary", []):
        lines.append(
            "| {number} | {type} | {confidence} | {area} | {competency} | {sources} | {organisations} | {families} |".format(
                number=_markdown_text(row.get("#", "")),
                type=_markdown_text(row.get("Type", "")),
                confidence=_markdown_text(row.get("Confidence", "")),
                area=_markdown_text(row.get("Sub functional area", "")),
                competency=_markdown_text(row.get("Competency", "")),
                sources=_markdown_text(row.get("Supporting sources", "")),
                organisations=_markdown_text(row.get("Supporting organisations", "")),
                families=_markdown_text(row.get("Source family types", "")),
            )
        )
    support_coverage = pack.get("support_coverage", {})
    if support_coverage:
        lines.extend(
            [
                "",
                "## Support coverage",
                "",
                "### Cited evidence by source family",
                "",
                "| Source family | Cited evidence count |",
                "| ------------- | -------------------- |",
            ]
        )
        for row in support_coverage.get("source_families", []):
            lines.append(f"| {_markdown_text(row.get('Source family', ''))} | {_markdown_text(row.get('Cited evidence count', ''))} |")
        lines.extend(["", "### Top cited organisations", "", "| Organisation | Cited evidence count |", "| ------------ | -------------------- |"])
        for row in support_coverage.get("organisations", [])[:10]:
            lines.append(f"| {_markdown_text(row.get('Organisation', ''))} | {_markdown_text(row.get('Cited evidence count', ''))} |")
    source_health = pack.get("source_health", [])
    if source_health:
        counts = pack.get("source_health_counts", {})
        lines.extend(
            [
                "",
                "## Source health",
                "",
                f"Healthy: {_markdown_text(counts.get('Healthy', 0))} · Low evidence: {_markdown_text(counts.get('Low evidence', 0))} · No evidence: {_markdown_text(counts.get('No evidence', 0))} · Errors: {_markdown_text(counts.get('Error', 0))}",
                "",
                "| Status | Evidence items | Organisation | Source | Suggested action |",
                "| ------ | -------------- | ------------ | ------ | ---------------- |",
            ]
        )
        for row in source_health:
            lines.append(
                "| {status} | {items} | {organisation} | {source} | {action} |".format(
                    status=_markdown_text(row.get("Status", "")),
                    items=_markdown_text(row.get("Evidence items", "")),
                    organisation=_markdown_text(row.get("Organisation", "")),
                    source=_markdown_text(row.get("Source", "")),
                    action=_markdown_text(row.get("Suggested action", "")),
                )
            )
    source_maintenance = pack.get("source_maintenance_recommendations", [])
    if source_maintenance:
        maintenance_counts = pack.get("source_maintenance_priority_counts", source_maintenance_priority_counts(source_maintenance))
        lines.extend(
            [
                "",
                "## Unhealthy or unuseful sources — review and replace",
                "",
                "These configured links need officer review. Suggested replacements are advisory and never update the catalogue automatically.",
                "",
                f"High priority: {_markdown_text(maintenance_counts.get('High', 0))} · Medium priority: {_markdown_text(maintenance_counts.get('Medium', 0))} · Low priority: {_markdown_text(maintenance_counts.get('Low', 0))}",
                "",
                "| Priority | Type | Organisation | Source | Current status | Current URL | Advice confidence | Replacement URLs | Provenance | Recommendation |",
                "| -------- | ---- | ------------ | ------ | -------------- | ----------- | ----------------- | ---------------- | ---------- | -------------- |",
            ]
        )
        for row in source_maintenance:
            lines.append(
                "| {priority} | {type} | {organisation} | {source} | {status} | {url} | {confidence} | {replacement_urls} | {provenance} | {recommendation} |".format(
                    priority=_markdown_text(row.get("Priority", "")),
                    type=_markdown_text(row.get("Recommendation type", "")),
                    organisation=_markdown_text(row.get("Organisation", "")),
                    source=_markdown_text(row.get("Source", "")),
                    status=_markdown_text(row.get("Current status", "")),
                    url=_markdown_text(row.get("Current URL", "")),
                    confidence=_markdown_text(row.get("Advice confidence", "")),
                    replacement_urls=_markdown_text(row.get("Recommended replacement URLs", "")),
                    provenance=_markdown_text(row.get("Provenance", "")),
                    recommendation=_markdown_text(row.get("Recommendation", "")),
                )
            )
    fallback_candidates = pack.get("llm_fallback_candidates", [])
    if fallback_candidates:
        readiness_counts = pack.get("llm_fallback_readiness_counts", {})
        lines.extend(
            [
                "",
                "## LLM fallback candidates",
                "",
                "These are fallback candidates that may need LLM-assisted recovery. Saved fallback recovery records, if any, are listed separately below.",
                "",
                f"Ready: {_markdown_text(readiness_counts.get('Ready for prompt review', 0))} · Access review: {_markdown_text(readiness_counts.get('Needs access review', 0))} · Optional signal: {_markdown_text(readiness_counts.get('Optional signal recovery', 0))} · Manual first: {_markdown_text((readiness_counts.get('Review manually first', 0) or 0) + (readiness_counts.get('Needs source URL', 0) or 0))}",
                "",
                "| Status | Readiness | Organisation | Source | Source URL | Recovery focus | Next step |",
                "| ------ | --------- | ------------ | ------ | ---------- | -------------- | --------- |",
            ]
        )
        for row in fallback_candidates:
            lines.append(
                "| {status} | {readiness} | {organisation} | {source} | {url} | {intent} | {next_step} |".format(
                    status=_markdown_text(row.get("Status", "")),
                    readiness=_markdown_text(row.get("Recovery readiness", "")),
                    organisation=_markdown_text(row.get("Organisation", "")),
                    source=_markdown_text(row.get("Source", "")),
                    url=_markdown_text(row.get("Source URL", "")),
                    intent=_markdown_text(row.get("Fallback intent", "")),
                    next_step=_markdown_text(row.get("Recommended next step", "")),
                )
            )
    fallback_recoveries = pack.get("llm_fallback_recoveries", [])
    if fallback_recoveries:
        lines.extend(
            [
                "",
                "## Saved LLM fallback recoveries",
                "",
                "These records came from explicit officer-triggered fallback recovery and remain separate from deterministic crawler evidence.",
                "",
                "| Record ID | Created | Organisation | Source | Recovered items | Source advice | Source URL |",
                "| --------- | ------- | ------------ | ------ | --------------- | ------------- | ---------- |",
            ]
        )
        for recovery in fallback_recoveries:
            lines.append(
                "| {record_id} | {created} | {organisation} | {source} | {count} | {advice} | {url} |".format(
                    record_id=_markdown_text(recovery.get("id", "")),
                    created=_markdown_text(recovery.get("created_at", "")),
                    organisation=_markdown_text(recovery.get("organisation", "")),
                    source=_markdown_text(recovery.get("source_name", "")),
                    count=_markdown_text(recovery.get("recovered_item_count", "")),
                    advice=_markdown_text(_source_maintenance_advice_summary(recovery.get("result", {}).get("source_maintenance_advice", {}))),
                    url=_markdown_text(recovery.get("source_url", "")),
                )
            )
    lines.extend(["", "## Recommendations", ""])
    for index, recommendation in enumerate(pack.get("recommendations", []), start=1):
        lines.extend(
            [
                f"### {index}. {_human_label(recommendation.get('recommendation_type', 'Recommendation')).title()} · {recommendation.get('confidence', 0):.0%}",
                "",
                f"Sub functional area: {_markdown_text(recommendation.get('sub_functional_area') or 'Not specified')}",
                f"Competency: {_markdown_text(recommendation.get('competency') or 'Not specified')}",
                f"Change suggested: {_markdown_text(recommendation.get('kind_of_changes_suggested') or 'Not specified')}",
                f"Support: {_markdown_text(recommendation.get('support_summary', 'Not specified'))}",
                "",
                "Reasons:",
                _markdown_text(recommendation.get("reasons_for_suggesting_the_changes") or recommendation.get("reasoning") or "Not specified"),
                "",
                "Supporting sources:",
            ]
        )
        supporting_sources = recommendation.get("supporting_sources") or _supporting_source_payload(
            recommendation.get("supporting_organisations", []),
            recommendation.get("supporting_urls", []),
            pack.get("source_lookup", {}),
            recommendation.get("supporting_evidence_ids", []),
        )
        for source in supporting_sources:
            provenance = ", ".join(
                _human_label(value)
                for value in (source.get("source_family"), source.get("source_type"), source.get("source_role"), source.get("country"))
                if value and value != "Unknown"
            )
            suffix = f" ({provenance})" if provenance else ""
            evidence_prefix = f"[Evidence {source.get('evidence_id')}] " if source.get("evidence_id") else ""
            title = f"{_markdown_text(source.get('title'))} — " if source.get("title") else ""
            lines.append(f"- {evidence_prefix}{title}{_markdown_text(source.get('organisation', 'Source'))}{suffix}: {_markdown_text(source.get('url', ''))}")
        lines.append("")
    saved_questions = pack.get("saved_questions", [])
    if saved_questions:
        summary = pack.get("question_history_summary", {})
        lines.extend(
            [
                "## Ask AI conversation summary",
                "",
                f"Questions: {_markdown_text(summary.get('question_count', len(saved_questions)))} · First: {_markdown_text(summary.get('first_question_at') or 'Unknown')} · Latest: {_markdown_text(summary.get('latest_question_at') or 'Unknown')}",
                f"Themes: {_markdown_text(', '.join(summary.get('common_review_themes', [])) or 'None detected')}",
                "",
            ]
        )
        lines.extend(["## Saved Ask AI questions", ""])
        for item in saved_questions:
            lines.extend(
                [
                    f"### {item.get('asked_at', 'Unknown')}",
                    "",
                    f"Question: {_markdown_text(item.get('question', ''))}",
                    "",
                    f"Answer: {_markdown_text(item.get('answer', ''))}",
                    "",
                ]
            )
    return "\n".join(lines).strip() + "\n"


def _question_history_markdown(question_history, batch_label: str) -> str:
    """Render saved Ask AI questions as a compact standalone Markdown transcript."""
    lines = ["# Ask AI Question History", "", f"Batch: {_markdown_text(batch_label)}", ""]
    summary = _question_history_summary(question_history)
    if summary["question_count"]:
        lines.extend(
            [
                "## Conversation summary",
                "",
                f"Questions: {_markdown_text(summary['question_count'])}",
                f"First question: {_markdown_text(summary['first_question_at'])}",
                f"Latest question: {_markdown_text(summary['latest_question_at'])}",
                f"Themes: {_markdown_text(', '.join(summary['common_review_themes']) or 'None detected')}",
                "",
            ]
        )
    for row in question_history:
        lines.extend(
            [
                f"## {_fmt(row['asked_at'])}",
                "",
                f"Question: {_markdown_text(row['question'])}",
                "",
                f"Answer: {_markdown_text(row['answer'])}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def render(services: dict) -> None:
    """Render the current-scan recommendation workspace."""
    st.header("Current Scan Recommendations")
    _show_credibility_legend()
    st.caption("AI recommendations are evidence-backed suggestions only. They never update the framework automatically, and this page always shows the latest current scan batch.")

    batches = services["recommendation_repository"].list_batches()
    if not batches:
        st.info("Run a scan first so the latest batch recommendations can appear here.")
        return

    selected_batch = batches[0]
    batch_id = selected_batch["id"]
    framework = services["framework_repository"].get(selected_batch["framework_version_id"]) if selected_batch else None
    recommendations = [
        item
        for item in services["recommendation_repository"].list_by_batch(batch_id)
        if item.recommendation_type not in HIDDEN_RECOMMENDATION_TYPES
    ]
    if not recommendations:
        st.info("This batch does not contain any visible recommendations.")
        return

    selected_run_id = selected_batch["scan_run_id"] if selected_batch and "scan_run_id" in selected_batch.keys() else None
    inferred_scan_link = False
    if selected_run_id is None:
        latest_runs = services["scan_repository"].list_runs(limit=1)
        if latest_runs and latest_runs[0].id is not None:
            selected_run_id = latest_runs[0].id
            inferred_scan_link = True
    selected_run = next((run for run in services["scan_repository"].list_runs(limit=50) if run.id == selected_run_id), None) if selected_run_id else None
    evidence_for_run = services["scan_repository"].list_evidence_for_run(selected_run_id) if selected_run_id else []
    evidence_by_id = {item.id: item for item in evidence_for_run if item.id is not None}
    source_lookup = {
        source.id: source
        for source in services["source_repository"].list_all()
        if source.id is not None
    }
    selected_family = st.selectbox("Filter supporting evidence by source family", _source_family_options(source_lookup))
    selected_type = st.selectbox("Filter supporting evidence by source type", _source_type_options(source_lookup))
    selected_family_key = selected_family.upper().replace(" ", "_")
    selected_type_key = selected_type.upper().replace(" ", "_")
    if selected_family != "All source families":
        recommendations = [
            recommendation
            for recommendation in recommendations
            if any(
                (source_lookup.get(evidence.source_id).source_family.value if source_lookup.get(evidence.source_id) else "") == selected_family_key
                for evidence in (evidence_by_id.get(eid) for eid in recommendation.supporting_evidence_ids)
                if evidence is not None
            )
        ]
        if not recommendations:
            st.info("No visible recommendations remain after applying the source-family filter.")
            return
    if selected_type != "All source types":
        recommendations = [
            recommendation
            for recommendation in recommendations
            if any(
                (source_lookup.get(evidence.source_id).source_type.value if source_lookup.get(evidence.source_id) else "") == selected_type_key
                for evidence in (evidence_by_id.get(eid) for eid in recommendation.supporting_evidence_ids)
                if evidence is not None
            )
        ]
        if not recommendations:
            st.info("No visible recommendations remain after applying the source-type filter.")
            return

    st.subheader("Batch summary")
    st.caption(f"Latest batch: {_fmt(selected_batch['created_at'])} · {_visible_count(batch_id, services['recommendation_repository'])} visible recommendation(s)")
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
            file_name=f"support_coverage_source_family_batch_{selected_run_id or batch_id}.csv",
            mime="text/csv",
        )
        coverage_right.caption("Top cited organisations")
        coverage_right.dataframe(organisation_rows[:10], hide_index=True, width="stretch")
        coverage_right.download_button(
            "Download organisation coverage (CSV)",
            data=_recommendation_summary_csv(organisation_rows),
            file_name=f"support_coverage_organisations_batch_{selected_run_id or batch_id}.csv",
            mime="text/csv",
        )
    source_health = _current_source_health_rows(selected_run, evidence_for_run, source_lookup)
    fallback_candidates = _current_fallback_candidates(selected_run, evidence_for_run, source_lookup)
    fallback_recoveries = services["fallback_recovery_repository"].list_for_scan_run(selected_run_id) if selected_run_id and "fallback_recovery_repository" in services else []
    source_maintenance = _current_combined_source_maintenance_recommendations(source_health, fallback_recoveries)
    if source_health:
        st.subheader("Source health")
        st.info(source_access_limits_note())
        health_counts = _source_health_status_counts(source_health)
        health_left, health_middle_left, health_middle_right, health_right = st.columns(4)
        health_left.metric("Healthy sources", health_counts["Healthy"])
        health_middle_left.metric("Low evidence", health_counts["Low evidence"])
        health_middle_right.metric("No evidence", health_counts["No evidence"])
        health_right.metric("Errors", health_counts["Error"])
        health_status_choice = st.selectbox(
            "Filter source health by status",
            ["All statuses", "Error", "No evidence", "Low evidence", "Healthy"],
            key=f"current_source_health_status_{selected_run_id or batch_id}",
        )
        visible_source_health = _filter_source_health_rows(source_health, health_status_choice)
        st.dataframe(visible_source_health, hide_index=True, width="stretch")
        st.download_button(
            "Download source health (CSV)",
            data=_recommendation_summary_csv(visible_source_health),
            file_name=f"source_health_batch_{selected_run_id or batch_id}.csv",
            mime="text/csv",
        )
        if fallback_candidates:
            with st.expander("Legacy source diagnostics (backend audit only)", expanded=False):
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
                    key=f"current_fallback_readiness_{selected_run_id or batch_id}",
                )
                visible_fallback_candidates = filter_fallback_candidates(fallback_candidates, readiness_choice)
                display_fallback_candidates = _badge_fallback_candidate_rows(visible_fallback_candidates)
                st.dataframe(display_fallback_candidates, hide_index=True, width="stretch")
                st.download_button(
                    "Download fallback candidate plan (CSV)",
                    data=_recommendation_summary_csv(display_fallback_candidates),
                    file_name=f"llm_fallback_candidates_batch_{selected_run_id or batch_id}.csv",
                    mime="text/csv",
                )
                prompt_left, prompt_right = st.columns(2)
                prompt_left.download_button(
                    "Download fallback request preview (JSON)",
                    data=json.dumps([fallback_prompt_payload(row) for row in visible_fallback_candidates], indent=2),
                    file_name=f"llm_fallback_request_preview_batch_{selected_run_id or batch_id}.json",
                    mime="application/json",
                )
                prompt_right.download_button(
                    "Download fallback prompt preview (Markdown)",
                    data="\n\n---\n\n".join(fallback_prompt_markdown(row) for row in visible_fallback_candidates),
                    file_name=f"llm_fallback_prompt_preview_batch_{selected_run_id or batch_id}.md",
                    mime="text/markdown",
                )
    st.subheader("Unhealthy or unuseful sources — review and replace")
    link_note = " The scan link was inferred from the latest scan because this older recommendation batch did not store one." if inferred_scan_link else ""
    st.caption(f"These configured links produced errors, no evidence, or low-value evidence in the selected scan batch ({_fmt(selected_batch['created_at'])}). Review the reason and replace the URL manually through Source Configuration if needed.{link_note}")
    if source_maintenance:
        maintenance_counts = source_maintenance_priority_counts(source_maintenance)
        high_col, medium_col, low_col = st.columns(3)
        high_col.metric("High priority", maintenance_counts["High"])
        medium_col.metric("Medium priority", maintenance_counts["Medium"])
        low_col.metric("Low priority", maintenance_counts["Low"])
        st.dataframe(source_maintenance, hide_index=True, width="stretch")
        remediation_repo = services.get("source_url_recommendation_repository")
        remediation_record = remediation_repo.get_for_batch(batch_id) if remediation_repo else None
        if remediation_record:
            st.success("AI URL recommendations have already been generated for this batch. The one-time request is locked.")
            try:
                saved_url_result = json.loads(remediation_record["raw_result"] or "{}")
                rows = []
                for source_item in saved_url_result.get("recommendations", []):
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
        elif services.get("source_url_recommender") and remediation_repo:
            st.info("You may make one fixed AI request for all flagged sources in this batch. Suggestions remain advisory and require manual approval.")
            if st.button("Generate AI replacement URLs for all flagged sources (one time)", key=f"generate_source_urls_{batch_id}", type="secondary"):
                try:
                    source_snapshot = [
                        {
                            "Organisation": row.get("Organisation", "Unknown"),
                            "Source": row.get("Source", "Unknown"),
                            "Current URL": row.get("Current URL", ""),
                            "Source family": row.get("Source family", "Unknown"),
                            "Source type": row.get("Source type", "Unknown"),
                            "Country": row.get("Country", "Unknown"),
                            "Crawler issue": row.get("Crawler issue", ""),
                        }
                        for row in source_maintenance
                    ]
                    with st.spinner("Asking OpenAI for same-organisation replacement URL suggestions..."):
                        url_result = services["source_url_recommender"].recommend(source_snapshot)
                    remediation_repo.add(selected_run_id, batch_id, "COMPLETED", source_snapshot, url_result)
                    st.success("AI URL recommendations saved for this batch. Review and apply any accepted URL manually in Source Configuration.")
                    st.dataframe(url_result.get("recommendations", []), hide_index=True, width="stretch")
                    st.rerun()
                except Exception as error:
                    st.error(str(error))
        st.download_button(
            "Download source maintenance recommendations (CSV)",
            data=_recommendation_summary_csv(source_maintenance),
            file_name=f"source_maintenance_recommendations_batch_{selected_run_id or batch_id}.csv",
            mime="text/csv",
        )
    else:
        if selected_run is None:
            st.warning(f"Source health is unavailable because no scan run could be linked to recommendation batch #{batch_id}.")
        else:
            st.success("No unhealthy or unuseful sources were flagged for the selected scan batch.")
    if False and fallback_recoveries:
        with st.expander("Saved LLM fallback recoveries", expanded=False):
            st.caption("🤖 LLM assisted · 🟡 Needs verification. These records came from explicit officer-triggered fallback recovery and remain separate from deterministic crawler evidence.")
            st.dataframe(_fallback_recovery_summary_rows(fallback_recoveries), hide_index=True, width="stretch")
            st.download_button(
                "Download saved fallback recoveries (JSON)",
                data=json.dumps(_fallback_recovery_payloads(fallback_recoveries), indent=2),
                file_name=f"llm_fallback_recoveries_batch_{selected_run_id or batch_id}.json",
                mime="application/json",
            )
            if "fallback_url_verifier" in services:
                for recovery in fallback_recoveries:
                    if st.button(f"Verify recovered URLs for record #{recovery.id}", key=f"current_verify_fallback_{recovery.id}"):
                        with st.spinner("Verifying recovered URLs with deterministic fetches..."):
                            verify_recovery_record(
                                recovery,
                                services["fallback_url_verifier"],
                                services["fallback_recovery_repository"],
                                services.get("operational_logger"),
                            )
                        st.success(f"Verification saved for fallback recovery record #{recovery.id}.")
                        st.rerun()
    st.subheader("Recommendation summary")
    st.caption("Use this table to triage which recommendations to inspect first. The detailed evidence remains in the expandable cards below.")
    summary_rows = _recommendation_summary_rows(recommendations, evidence_by_id, source_lookup)
    st.dataframe(
        summary_rows,
        hide_index=True,
        width="stretch",
    )
    st.download_button(
        "Download recommendation summary (CSV)",
        data=_recommendation_summary_csv(summary_rows),
        file_name=f"recommendation_summary_batch_{selected_run_id or batch_id}.csv",
        mime="text/csv",
    )
    question_history = services["batch_question_repository"].list_by_batch(batch_id)
    recommendation_pack = _build_recommendation_pack(
        selected_run_id,
        selected_batch,
        framework,
        evidence_for_run,
        recommendations,
        source_lookup,
        question_history,
        source_health,
        fallback_candidates,
        fallback_recoveries,
        source_maintenance,
    )
    st.download_button(
        "Download recommendation pack (JSON)",
        data=json.dumps(recommendation_pack, indent=2),
        file_name=f"recommendation_pack_batch_{selected_run_id or batch_id}.json",
        mime="application/json",
    )
    st.download_button(
        "Download recommendation pack (Markdown)",
        data=_recommendation_pack_markdown(recommendation_pack),
        file_name=f"recommendation_pack_batch_{selected_run_id or batch_id}.md",
        mime="text/markdown",
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
                    evidence = evidence_by_id.get(evidence_id)
                    if evidence:
                        source = source_lookup.get(evidence.source_id)
                        with st.expander(f"Evidence {evidence.id} · {evidence.title} · {evidence.organisation}"):
                            label = _credibility_label(evidence.evidence_type)
                            badge = _credibility_badge(label)
                            source_badge = _source_type_badge(source.source_type.value if source else "")
                            role_badge = _source_role_badge(source.source_role.value if source else "")
                            st.caption(f"Evidence ID: {evidence.id}")
                            st.caption(f"{badge} {label} · {source_badge} · {role_badge} · {_human_label(evidence.evidence_type)} · Published: {evidence.publication_date or 'Unavailable'}")
                            st.markdown(f"[Open supporting source]({evidence.url})")
                            st.code(evidence.article_text, language="text")
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

    if question_history:
        summary = _question_history_summary(question_history)
        st.subheader("Ask AI conversation summary")
        summary_left, summary_middle, summary_right = st.columns(3)
        summary_left.metric("Questions", summary["question_count"])
        summary_middle.metric("First question", summary["first_question_at"] or "Unknown")
        summary_right.metric("Latest question", summary["latest_question_at"] or "Unknown")
        st.caption(f"Common review themes: {', '.join(summary['common_review_themes']) if summary['common_review_themes'] else 'None detected yet'}")
        st.subheader("Saved batch questions")
        batch_label = _fmt(selected_batch["created_at"]) if selected_batch else "latest"
        question_export_left, question_export_right = st.columns(2)
        question_export_left.download_button(
            "Download Q&A history (CSV)",
            data=_question_history_csv(question_history),
            file_name=f"ask_ai_questions_{batch_id}.csv",
            mime="text/csv",
        )
        question_export_right.download_button(
            "Download Q&A history (Markdown)",
            data=_question_history_markdown(question_history, batch_label),
            file_name=f"ask_ai_questions_{batch_id}.md",
            mime="text/markdown",
        )
        for row in question_history:
            with st.expander(f"{_fmt(row['asked_at'])} · {row['question'][:80]}"):
                st.markdown("**Question**")
                st.write(row["question"])
                st.markdown("**Answer**")
                st.write(row["answer"])
                st.caption("Stored with the batch context snapshot for audit and traceability.")

    st.subheader("Ask a focused question about this recommendation batch")
    st.info(
        "Ask AI is a batch review assistant, not a general chatbot. It uses this recommendation batch, evidence previews, framework snapshot, source diagnostics, and up to the latest "
        f"{ASK_AI_RECENT_QA_LIMIT} saved Q&A turns from this batch only. For best results, ask one precise review question at a time."
    )
    st.caption("Context scope: recommendations · cited evidence previews only (not the full scan) · framework snapshot · diagnostic summary counts · recent same-batch Q&A. Uncited evidence and detailed source diagnostics are not sent to Ask AI.")
    st.caption("Focused question examples")
    starter_columns = st.columns(len(ASK_AI_QUESTION_STARTERS))
    for index, starter in enumerate(ASK_AI_QUESTION_STARTERS):
        if starter_columns[index].button(starter, key=f"ask_ai_starter_{index}", width="stretch"):
            st.session_state["ask_ai_query"] = starter
    query = st.text_area(
        "Focused batch-review question",
        key="ask_ai_query",
        placeholder="Example: Why is Recommendation 1 suggested, and which evidence IDs should I check first?",
    )
    if st.button("Ask AI", type="secondary", disabled=not query.strip()):
        try:
            with st.spinner("Asking AI to review this batch context..."):
                evidence_for_context = services["scan_repository"].list_evidence_for_run(selected_run_id) if selected_run_id else []
                context = _build_question_context(selected_run_id, selected_batch, framework, evidence_for_context, recommendations, source_lookup, source_health, question_history=question_history)
                context = _compact_live_question_context(context)
                answer = services["recommendation_service"].answer_question(context, query)
                services["batch_question_repository"].add(batch_id, query, answer, json.dumps(context), datetime.now().astimezone())
            st.success("Question answered and logged for this batch.")
            st.markdown(answer)
        except RecommendationError as error:
            st.error(str(error))
