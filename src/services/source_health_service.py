"""Shared source-health helpers for scan quality review."""
from collections import Counter
import json
import re

from src.models.domain import Source

LOW_EVIDENCE_THRESHOLD = 5
FALLBACK_READINESS_READY = "Ready for prompt review"
FALLBACK_READINESS_ACCESS = "Needs access review"
FALLBACK_READINESS_SIGNAL = "Optional signal recovery"
FALLBACK_READINESS_MANUAL = "Review manually first"
FALLBACK_READINESS_SOURCE_URL = "Needs source URL"
FALLBACK_READINESS_ALL = "All readiness levels"
FALLBACK_READINESS_FILTER_OPTIONS = [
    FALLBACK_READINESS_ALL,
    FALLBACK_READINESS_READY,
    FALLBACK_READINESS_ACCESS,
    FALLBACK_READINESS_SIGNAL,
    FALLBACK_READINESS_MANUAL,
    FALLBACK_READINESS_SOURCE_URL,
]

SOURCE_ACCESS_LIMITS_NOTE = (
    "Access note: some approved public websites block automated crawling through robots.txt, "
    "Cloudflare/security challenges, cookie walls, login/paywall controls, timeouts, or managed-network "
    "proxy/TLS inspection. The prototype may try normal requests, source-specific URLs, bounded retries, "
    "browser rendering, and PDF extraction where permitted, but it does not bypass security controls. "
    "Blocked or low-quality sources should be reviewed through source health, Source Configuration, or governed LLM fallback."
)


def infer_source_type_from_url(url: str) -> str:
    """Infer a conservative source type from a configured URL path."""
    lowered = str(url or "").casefold()
    if any(token in lowered for token in ("standard", "framework", "competenc", "code-of-practice", "codes-and-standards", "attributes")):
        return "FRAMEWORK"
    if any(token in lowered for token in ("course", "programme", "program", "catalog", "education", "training", "certification", "curriculum", "degree")):
        return "CATALOGUE"
    if any(token in lowered for token in ("research", "journal", "publication", "report", "knowledge", "resources", "handbook")):
        return "INDEX"
    if any(token in lowered for token in ("news", "media", "blog", "press-release", "insights", "topic")):
        return "TREND"
    return "ARTICLE"


def source_access_limits_note() -> str:
    """Return the standard officer/IT explanation for crawler access limits."""
    return SOURCE_ACCESS_LIMITS_NOTE


def source_health_action(status: str, llm_allowed: bool) -> str:
    """Return a plain-language action suggestion for one source-health status."""
    if status == "Healthy":
        return "Keep current crawler"
    if status == "Low evidence":
        return "Review source URL or article limits"
    if status == "No evidence":
        return "Consider LLM fallback" if llm_allowed else "Tune or disable source"
    if status == "Error":
        return "Consider LLM fallback" if llm_allowed else "Fix access or disable source"
    return "Review source"


def source_maintenance_recommendations(source_health: list[dict]) -> list[dict]:
    """Return deterministic source-link maintenance suggestions for officer review.

    These are catalogue-quality recommendations only. They do not change the
    configured source catalogue and they do not call an LLM.
    """
    recommendations = []
    for row in source_health or []:
        status = row.get("Status", "Unknown")
        if status == "Healthy":
            continue
        recommendation_type, priority, recommendation = _source_maintenance_action(row)
        recommendations.append(
            {
                "Priority": priority,
                "Recommendation type": recommendation_type,
                "Organisation": row.get("Organisation", "Unknown"),
                "Source": row.get("Source", "Unknown"),
                "Current URL": row.get("Source URL", ""),
                "Source family": row.get("Source family", "Unknown"),
                "Source type": row.get("Source type", "Unknown"),
                "Source role": row.get("Source role", "Unknown"),
                "Country": row.get("Country", "Unknown"),
                "Current status": status,
                "Evidence items": row.get("Evidence items", 0),
                "Crawler issue": row.get("Reason", "No detailed crawler issue captured"),
                "Recommendation": recommendation,
                "Suggested action": row.get("Suggested action", "Review source"),
                "Advice confidence": "",
                "Recommended replacement URLs": "",
                "Requires officer approval": "Yes",
                "Provenance": "Deterministic source-health rule",
                "Officer instruction": "Review this source and replace the configured URL manually if it is not useful.",
                "AI URL recommendation": "Available on request",
            }
        )
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(
        recommendations,
        key=lambda item: (
            priority_order.get(item["Priority"], 9),
            item["Organisation"],
            item["Source"],
        ),
    )


def fallback_source_maintenance_recommendations(fallback_recoveries: list | None) -> list[dict]:
    """Return source-maintenance rows from saved governed LLM fallback advice.

    These rows are advisory only. They make LLM-suggested source-link
    improvements visible in the same shape as deterministic source-health
    recommendations, while preserving provenance.
    """
    rows = []
    for recovery in fallback_recoveries or []:
        try:
            payload = json.loads(getattr(recovery, "raw_result", "{}") or "{}")
        except json.JSONDecodeError:
            payload = {}
        advice = payload.get("source_maintenance_advice", {})
        if not isinstance(advice, dict) or not advice:
            continue
        recommendation_type = str(advice.get("recommendation_type", "NO_CLEAR_ADVICE"))
        if recommendation_type in {"KEEP_CURRENT_SOURCE", "NO_CLEAR_ADVICE"}:
            continue
        urls = advice.get("recommended_replacement_urls") or []
        confidence = advice.get("confidence")
        rows.append(
            {
                "Priority": _fallback_advice_priority(recommendation_type),
                "Recommendation type": recommendation_type.replace("_", " ").title().replace("Url", "URL").replace("It", "IT").replace("Pdf", "PDF"),
                "Organisation": getattr(recovery, "organisation", "Unknown"),
                "Source": getattr(recovery, "source_name", "Unknown"),
                "Current URL": getattr(recovery, "source_url", ""),
                "Source family": "Unknown",
                "Source type": "Unknown",
                "Source role": "Unknown",
                "Country": "Unknown",
                "Current status": "LLM fallback advice",
                "Evidence items": getattr(recovery, "recovered_item_count", 0),
                "Crawler issue": "See saved fallback recovery record",
                "Recommendation": str(advice.get("reason", "")).strip() or "Review this source based on fallback recovery advice.",
                "Suggested action": "Review and apply manually through Source Configuration",
                "Advice confidence": f"{float(confidence):.0%}" if isinstance(confidence, (float, int)) else "",
                "Recommended replacement URLs": ", ".join(str(url) for url in urls),
                "Requires officer approval": "Yes",
                "Provenance": "LLM-assisted fallback source advice",
                "Officer instruction": "Review the suggested URL and apply any replacement manually in Source Configuration.",
                "AI URL recommendation": "Already suggested by fallback review",
            }
        )
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(rows, key=lambda item: (priority_order.get(item["Priority"], 9), item["Organisation"], item["Source"]))


def combined_source_maintenance_recommendations(source_health: list[dict], fallback_recoveries: list | None = None) -> list[dict]:
    """Return deterministic and LLM-assisted source-maintenance advice together."""
    return source_maintenance_recommendations(source_health) + fallback_source_maintenance_recommendations(fallback_recoveries)


def source_maintenance_priority_counts(recommendations: list[dict]) -> dict[str, int]:
    """Count source-maintenance recommendations by officer-facing priority."""
    counts = Counter(row.get("Priority", "Low") for row in recommendations or [])
    return {
        "High": counts.get("High", 0),
        "Medium": counts.get("Medium", 0),
        "Low": counts.get("Low", 0),
    }


def _fallback_advice_priority(recommendation_type: str) -> str:
    """Map LLM source-maintenance advice into simple officer-facing priority."""
    if recommendation_type in {"REPLACE_SOURCE_URL", "DISABLE_SOURCE", "NEEDS_IT_ACCESS_REVIEW"}:
        return "High"
    if recommendation_type in {"USE_BROWSER_RENDERING", "USE_PDF_OR_RESOURCE_HUB"}:
        return "Medium"
    return "Low"


def _source_maintenance_action(row: dict) -> tuple[str, str, str]:
    """Classify one source-health row into a source-maintenance recommendation."""
    status = row.get("Status", "Unknown")
    llm_allowed = row.get("LLM fallback allowed") == "Yes"
    source_type = str(row.get("Source type", "")).upper()
    if status == "Error":
        return (
            "Access or source URL review",
            "High",
            "Check whether this URL is blocked, obsolete, cookie-restricted, or needs IT/proxy access review. If access remains blocked, find a better official source URL or disable the source.",
        )
    if status == "No evidence" and llm_allowed:
        return (
            "Fallback or replacement URL review",
            "High",
            "Review the fallback prompt preview and look for a more direct official competency, course, framework, standards, or resource URL before spending tokens.",
        )
    if status == "No evidence":
        return (
            "Replacement URL or disable review",
            "High",
            "Find a more direct official source URL or disable this source if it no longer contributes useful STE evidence.",
        )
    if status == "Low evidence" and any(token in source_type for token in ("FRAMEWORK", "CATALOGUE", "INDEX")):
        return (
            "Improve configured source URL",
            "Medium",
            "This structured source produced very few records. Check whether a deeper listing page, PDF/report page, course catalogue, or standards index would be a better configured URL.",
        )
    if status == "Low evidence":
        return (
            "Review article limits or source relevance",
            "Low",
            "This source produced only a small amount of evidence. Keep it if the content is useful, otherwise tune article/listing limits or replace it with a more relevant page.",
        )
    return (
        "Manual source review",
        "Low",
        "Review whether this configured source still contributes useful STE competency intelligence.",
    )


def _source_has_error(error_summary: str, name: str) -> bool:
    """Match workflow's source-prefixed errors, not names inside URLs or prose."""
    if not error_summary or not name:
        return False
    return bool(re.search(r'(?:^|;\s*|\n\s*)' + re.escape(name) + r'\s*:',
                          error_summary, flags=re.IGNORECASE))


def source_health_rows(run, evidence: list, source_lookup: dict[int, Source] | None = None) -> list[dict]:
    """Summarise per-source output quality for one scan batch."""
    if run is None:
        return []
    source_lookup = source_lookup or {}
    sources_by_url = {source.url: source for source in source_lookup.values()}
    sources_by_name = {source.name: source for source in source_lookup.values()}
    evidence_counts = Counter(item.source_id for item in evidence)
    error_text = (run.error_summary or "").casefold()
    rows = []
    for index, source in enumerate(run.sources_snapshot or (), start=1):
        source_id = source.get("id")
        if source_id is None:
            matched_source = sources_by_url.get(source.get("url")) or sources_by_name.get(source.get("name"))
            source_id = matched_source.id if matched_source else None
        count = evidence_counts.get(source_id, 0)
        name = source.get("name", f"Source {index}")
        organisation = source.get("organisation", "Unknown")
        has_error = _source_has_error(error_text, str(name))
        if has_error:
            status = "Error"
        elif count == 0:
            status = "No evidence"
        elif count < LOW_EVIDENCE_THRESHOLD:
            status = "Low evidence"
        else:
            status = "Healthy"
        llm_allowed = bool(source.get("llm_allowed", True))
        rows.append(
            {
                "Status": status,
                "Evidence items": count,
                "Source family": source.get("source_family", "Unknown"),
                "Source type": source.get("source_type", "Unknown"),
                "Source role": source.get("source_role", "Unknown"),
                "Organisation": organisation,
                "Source": name,
                "Source URL": source.get("url", ""),
                "Country": source.get("country", "Unknown"),
                "Reason": "Crawler error or access issue" if has_error else ("Crawler produced no retained evidence" if count == 0 else "Evidence output below source-health threshold" if count < LOW_EVIDENCE_THRESHOLD else "Source produced enough retained evidence"),
                "LLM fallback allowed": "Yes" if llm_allowed else "No",
                "Suggested action": source_health_action(status, llm_allowed),
            }
        )
    status_order = {"Error": 0, "No evidence": 1, "Low evidence": 2, "Healthy": 3}
    return sorted(rows, key=lambda row: (status_order.get(row["Status"], 9), -row["Evidence items"], row["Organisation"], row["Source"]))


def source_fallback_candidates(run, evidence: list, source_lookup: dict[int, Source] | None = None) -> list[dict]:
    """Return sources that are eligible for a future LLM-assisted recovery pass.

    This is an audit/planning helper only. It does not call an LLM or crawl the web.
    """
    if run is None:
        return []
    source_lookup = source_lookup or {}
    sources_by_url = {source.url: source for source in source_lookup.values()}
    sources_by_name = {source.name: source for source in source_lookup.values()}
    evidence_counts = Counter(item.source_id for item in evidence)
    error_text = run.error_summary or ""
    candidates = []
    for index, source in enumerate(run.sources_snapshot or (), start=1):
        source_id = source.get("id")
        if source_id is None:
            matched_source = sources_by_url.get(source.get("url")) or sources_by_name.get(source.get("name"))
            source_id = matched_source.id if matched_source else None
        count = evidence_counts.get(source_id, 0)
        name = source.get("name", f"Source {index}")
        organisation = source.get("organisation", "Unknown")
        has_error = _source_has_error(error_text, str(name))
        if has_error:
            status = "Error"
        elif count == 0:
            status = "No evidence"
        elif count < LOW_EVIDENCE_THRESHOLD:
            status = "Low evidence"
        else:
            status = "Healthy"
        if status not in {"Error", "No evidence"} or not bool(source.get("llm_allowed", True)):
            continue
        source_type = source.get("source_type", "ARTICLE")
        source_role = source.get("source_role", "PRIMARY_DISCOVERY")
        readiness, readiness_reason = _fallback_readiness(status, source.get("url", ""), source_type, source_role)
        next_step = _fallback_next_step(readiness)
        candidates.append(
            {
                "Status": status,
                "Organisation": organisation,
                "Source": name,
                "Source URL": source.get("url", ""),
                "Source family": source.get("source_family", "Unknown"),
                "Source type": source_type,
                "Source role": source_role,
                "Country": source.get("country", "Unknown"),
                "Evidence items": count,
                "Fallback intent": _fallback_intent(source_type, source_role),
                "Recovery readiness": readiness,
                "Readiness reason": readiness_reason,
                "Recommended next step": next_step,
                "Reason": "Crawler error or access issue" if status == "Error" else "Crawler produced no retained evidence",
            }
        )
    status_order = {"Error": 0, "No evidence": 1}
    return sorted(candidates, key=lambda row: (status_order.get(row["Status"], 9), row["Organisation"], row["Source"]))


def _fallback_intent(source_type: str, source_role: str) -> str:
    """Describe what a future fallback prompt should recover from the source."""
    source_type = str(source_type or "").upper()
    source_role = str(source_role or "").upper()
    if source_type == "FRAMEWORK":
        return "Recover explicit STE competency, standards, or framework concepts"
    if source_type == "CATALOGUE":
        return "Recover STE courses, programmes, certifications, or training resources"
    if source_type == "INDEX":
        return "Recover linked STE capability, research, resource, or programme pages"
    if source_type == "TREND" or source_role == "TREND_VALIDATION":
        return "Recover STE trend or outlier signals as supporting evidence only"
    return "Recover relevant STE evidence while preserving source URLs"


def _fallback_readiness(status: str, source_url: str, source_type: str, source_role: str) -> tuple[str, str]:
    """Classify whether a candidate is ready for future fallback recovery review."""
    if not source_url:
        return FALLBACK_READINESS_SOURCE_URL, "No source URL was captured in the batch snapshot."
    source_type = str(source_type or "").upper()
    source_role = str(source_role or "").upper()
    if status == "Error":
        return FALLBACK_READINESS_ACCESS, "The source errored during deterministic crawling; check access, robots, cookies, or proxy constraints before a fallback call."
    if source_type in {"FRAMEWORK", "CATALOGUE", "INDEX"}:
        return FALLBACK_READINESS_READY, "The source has a structured intent and no retained evidence, so a controlled fallback prompt can be reviewed."
    if source_type == "TREND" or source_role == "TREND_VALIDATION":
        return FALLBACK_READINESS_SIGNAL, "The source is mainly a signal source; fallback should recover outlier/trend evidence only if officers still need it."
    return FALLBACK_READINESS_MANUAL, "The source is article-like or loosely structured, so confirm it is worth fallback recovery before spending tokens."


def _fallback_next_step(readiness: str) -> str:
    """Return a plain-language next step for one fallback-readiness label."""
    if readiness == FALLBACK_READINESS_READY:
        return "Review the fallback prompt preview, then decide whether to run a controlled LLM recovery pass."
    if readiness == FALLBACK_READINESS_ACCESS:
        return "Check network, robots, cookies, proxy, or source URL access before attempting fallback recovery."
    if readiness == FALLBACK_READINESS_SIGNAL:
        return "Run fallback only if officers need extra trend or outlier signals from this source."
    if readiness == FALLBACK_READINESS_SOURCE_URL:
        return "Restore or correct the source URL in the source configuration before fallback review."
    if readiness == FALLBACK_READINESS_MANUAL:
        return "Confirm the source is important enough for fallback recovery before spending tokens."
    return "Review the source before deciding the next action."


def fallback_prompt_payload(candidate: dict) -> dict:
    """Build a reviewable future LLM fallback request for one candidate source.

    The payload is intentionally JSON-safe and does not execute any model call.
    """
    source_type = str(candidate.get("Source type", "ARTICLE") or "ARTICLE").upper()
    source_role = str(candidate.get("Source role", "PRIMARY_DISCOVERY") or "PRIMARY_DISCOVERY").upper()
    return {
        "mode": "llm_fallback_recovery_preview",
        "source": {
            "organisation": candidate.get("Organisation", "Unknown"),
            "name": candidate.get("Source", "Unknown"),
            "url": candidate.get("Source URL", ""),
            "country": candidate.get("Country", "Unknown"),
            "source_family": candidate.get("Source family", "Unknown"),
            "source_type": source_type,
            "source_role": source_role,
        },
        "scan_health": {
            "status": candidate.get("Status", "Unknown"),
            "evidence_items": candidate.get("Evidence items", 0),
            "reason": candidate.get("Reason", "Unknown"),
            "recovery_readiness": candidate.get("Recovery readiness", "Unknown"),
            "readiness_reason": candidate.get("Readiness reason", "Unknown"),
            "recommended_next_step": candidate.get("Recommended next step", "Review the source before deciding the next action."),
        },
        "recovery_objective": candidate.get("Fallback intent") or _fallback_intent(source_type, source_role),
        "constraints": [
            "Use only Science, Technology, and Engineering evidence.",
            "Preserve source URLs and organisation provenance.",
            "Prefer explicit competencies, standards, courses, programmes, certifications, research capability pages, and official guidance.",
            "Treat news or publications as supporting trend/outlier signals, not primary competency definitions.",
            "Do not invent source URLs, organisations, courses, competencies, or standards.",
            "If the source cannot be reliably recovered, return an explicit low-confidence/no-recovery result.",
        ],
        "expected_output": {
            "organisation": "string",
            "source_url": "string",
            "recovered_items": [
                {
                    "title": "string",
                    "url": "string",
                    "evidence_class": "competency_or_standard | course_programme_or_resource | research_or_capability | signal_or_topic",
                    "summary": "string",
                    "explicit_or_inferred": "EXPLICIT | INFERRED",
                    "confidence": "number from 0 to 1",
                }
            ],
            "source_maintenance_advice": {
                "recommendation_type": "KEEP_CURRENT_SOURCE | REPLACE_SOURCE_URL | DISABLE_SOURCE | NEEDS_IT_ACCESS_REVIEW | USE_BROWSER_RENDERING | USE_PDF_OR_RESOURCE_HUB | NO_CLEAR_ADVICE",
                "recommended_replacement_urls": ["https://official.example/better-source"],
                "reason": "string",
                "confidence": "number from 0 to 1",
            },
            "recovery_notes": "string",
        },
    }


def fallback_prompt_markdown(candidate: dict) -> str:
    """Return a human-readable fallback prompt preview for officer/IT review."""
    payload = fallback_prompt_payload(candidate)
    source = payload["source"]
    health = payload["scan_health"]
    lines = [
        "# LLM Fallback Recovery Prompt Preview",
        "",
        "This is a preview only. The prototype has not called the LLM for this fallback source.",
        "",
        "## Source",
        "",
        f"- Organisation: {source['organisation']}",
        f"- Source: {source['name']}",
        f"- URL: {source['url']}",
        f"- Country: {source['country']}",
        f"- Source family: {source['source_family']}",
        f"- Source type: {source['source_type']}",
        f"- Source role: {source['source_role']}",
        "",
        "## Scan health",
        "",
        f"- Status: {health['status']}",
        f"- Evidence items: {health['evidence_items']}",
        f"- Reason: {health['reason']}",
        f"- Recovery readiness: {health['recovery_readiness']}",
        f"- Readiness reason: {health['readiness_reason']}",
        f"- Recommended next step: {health['recommended_next_step']}",
        "",
        "## Recovery objective",
        "",
        payload["recovery_objective"],
        "",
        "## Instructions for a future LLM fallback pass",
        "",
        "Review the source above and recover only relevant STE competency intelligence. "
        "Organise any useful material into explicit competencies/standards, courses/programmes/resources, "
        "research/capability evidence, or supporting trend/outlier signals. Preserve URLs and provenance. "
        "Do not invent unavailable evidence.",
        "",
        "## Constraints",
        "",
    ]
    lines.extend(f"- {constraint}" for constraint in payload["constraints"])
    lines.extend(["", "## Expected JSON output shape", "", "```json", json.dumps(payload["expected_output"], indent=2), "```"])
    return "\n".join(lines)


def fallback_readiness_counts(candidates: list[dict]) -> dict[str, int]:
    """Count fallback candidates by recovery-readiness label."""
    counts = Counter(row.get("Recovery readiness", "Unknown") for row in candidates or [])
    return {
        FALLBACK_READINESS_READY: counts.get(FALLBACK_READINESS_READY, 0),
        FALLBACK_READINESS_ACCESS: counts.get(FALLBACK_READINESS_ACCESS, 0),
        FALLBACK_READINESS_SIGNAL: counts.get(FALLBACK_READINESS_SIGNAL, 0),
        FALLBACK_READINESS_MANUAL: counts.get(FALLBACK_READINESS_MANUAL, 0),
        FALLBACK_READINESS_SOURCE_URL: counts.get(FALLBACK_READINESS_SOURCE_URL, 0),
    }


def filter_fallback_candidates(candidates: list[dict], readiness_choice: str) -> list[dict]:
    """Filter fallback candidates by recovery-readiness label."""
    if readiness_choice == FALLBACK_READINESS_ALL:
        return candidates
    return [row for row in candidates if row.get("Recovery readiness") == readiness_choice]


def automatic_fallback_queue(candidates: list[dict], limit: int = 3) -> list[dict]:
    """Return bounded candidates eligible for future governed auto-recovery."""
    if limit < 1:
        return []
    eligible = [row for row in candidates if row.get("Recovery readiness") == FALLBACK_READINESS_READY]
    return [dict(row, **{"Queue status": "Eligible for governed automatic recovery"}) for row in eligible[:limit]]


def replacement_url_prompt_payload(row: dict) -> dict:
    """Build the fixed, organisation-preserving prompt contract for URL advice."""
    organisation = str(row.get("Organisation", "Unknown") or "Unknown")
    return {
        "mode": "source_url_recommendation",
        "organisation": organisation,
        "current_source": {
            "name": row.get("Source", "Unknown"),
            "url": row.get("Current URL") or row.get("Source URL", ""),
            "family": row.get("Source family", "Unknown"),
            "type": row.get("Source type", "Unknown"),
            "country": row.get("Country", "Unknown"),
            "crawler_issue": row.get("Crawler issue", row.get("Reason", "")),
        },
        "fixed_instructions": [
            "Keep the organisation exactly unchanged.",
            "Recommend only public HTTPS URLs belonging to that same organisation.",
            "Prefer official STE competency, course, programme, framework, standards, research, or resource pages.",
            "Do not invent URLs and do not recommend a different organisation.",
            "Return exact URLs with a short reason; suggestions require human review and must not update the catalogue automatically.",
        ],
    }


def replacement_url_prompt_markdown(row: dict) -> str:
    """Render the fixed URL-advice contract for officer/IT review."""
    payload = replacement_url_prompt_payload(row)
    source = payload["current_source"]
    instructions = "\n".join(f"- {item}" for item in payload["fixed_instructions"])
    return (
        "# AI replacement URL recommendation preview\n\n"
        f"- Organisation: {payload['organisation']}\n"
        f"- Current source: {source['name']}\n"
        f"- Current URL: {source['url']}\n"
        f"- Crawler issue: {source['crawler_issue']}\n\n"
        "## Fixed instructions\n\n"
        f"{instructions}\n"
    )


def source_health_status_counts(rows: list[dict]) -> dict[str, int]:
    """Count source-health statuses for compact officer-facing metrics."""
    counts = Counter(row.get("Status", "Unknown") for row in rows or [])
    return {
        "Healthy": counts.get("Healthy", 0),
        "Low evidence": counts.get("Low evidence", 0),
        "No evidence": counts.get("No evidence", 0),
        "Error": counts.get("Error", 0),
    }


def filter_source_health_rows(rows: list[dict], status_choice: str) -> list[dict]:
    """Filter source-health rows by status while preserving the full default view."""
    if status_choice == "All statuses":
        return rows
    return [row for row in rows if row.get("Status") == status_choice]
