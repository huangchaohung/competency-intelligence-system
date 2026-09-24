import json
import pytest
from datetime import datetime
from types import SimpleNamespace
from src.services.source_health_service import _source_has_error


@pytest.mark.parametrize('name,expected', [('PUB', False), ('PUB Research', False),
                                         ('INCOSE', True), ('NUS', False), ('NUS Courses', True)])
def test_error_attribution_does_not_match_organisation_substrings(name, expected):
    summary = 'INCOSE: 403 for https://www.incose.org/publish-with-incose; NUS Courses: timeout'
    assert _source_has_error(summary, name) is expected


def test_health_keeps_other_sources_from_same_organisation_separate():
    run = SimpleNamespace(error_summary='PUB Other: timeout; INCOSE: publish-with-incose',
                          sources_snapshot=[{'id': 1, 'name': 'PUB Research', 'organisation': 'PUB'},
                                            {'id': 2, 'name': 'PUB Other', 'organisation': 'PUB'}])
    evidence = [SimpleNamespace(source_id=1)]
    rows = {row['Source']: row for row in source_health_rows(run, evidence)}
    assert rows['PUB Research']['Status'] == 'Low evidence'
    assert rows['PUB Other']['Status'] == 'Error'

from src.models.domain import Evidence, Source, SourceFamily
from src.services.source_health_service import FALLBACK_READINESS_FILTER_OPTIONS, FALLBACK_READINESS_READY, automatic_fallback_queue, combined_source_maintenance_recommendations, fallback_source_maintenance_recommendations, filter_fallback_candidates, filter_source_health_rows, fallback_prompt_markdown, fallback_prompt_payload, fallback_readiness_counts, infer_source_type_from_url, replacement_url_prompt_markdown, replacement_url_prompt_payload, source_access_limits_note, source_fallback_candidates, source_health_action, source_health_rows, source_health_status_counts, source_maintenance_priority_counts, source_maintenance_recommendations


def test_source_health_rows_include_zero_output_and_error_sources() -> None:
    """Shared source-health rules include configured sources even without evidence."""
    run = SimpleNamespace(
        error_summary="Broken Source: 403 Client Error",
        sources_snapshot=[
            {"id": 1, "name": "Strong Source", "organisation": "Org A", "source_family": "PROFESSIONAL_BODY", "source_type": "FRAMEWORK", "source_role": "PRIMARY_DISCOVERY"},
            {"id": 2, "name": "Broken Source", "organisation": "Org B", "source_family": "GOVERNMENT_AGENCY", "source_type": "TREND", "source_role": "TREND_VALIDATION"},
            {"name": "Quiet Source", "url": "https://quiet.example", "organisation": "Org C", "source_family": "HIGHER_LEARNING", "source_type": "CATALOGUE", "source_role": "SUPPORTING_DISCOVERY", "llm_allowed": False},
            {"id": 4, "name": "Empty Source", "organisation": "Org D", "source_family": "PROFESSIONAL_BODY", "source_type": "FRAMEWORK", "source_role": "PRIMARY_DISCOVERY", "llm_allowed": False},
        ],
    )
    evidence = [
        Evidence(index, 7, 1, "EXPLICIT_COMPETENCY", f"Evidence {index}", None, "Org A", f"https://a.example/{index}", "text", datetime.now())
        for index in range(1, 6)
    ] + [
        Evidence(6, 7, 3, "COURSE", "Quiet course", None, "Org C", "https://quiet.example/course", "text", datetime.now())
    ]
    source_lookup = {
        3: Source(3, "Quiet Source", "https://quiet.example", "Org C", source_family=SourceFamily.HIGHER_LEARNING),
    }

    rows = source_health_rows(run, evidence, source_lookup)

    assert rows[0]["Status"] == "Error"
    assert rows[0]["Source URL"] == ""
    assert rows[0]["Reason"] == "Crawler error or access issue"
    assert rows[0]["Suggested action"] == "Consider LLM fallback"
    assert rows[1]["Status"] == "No evidence"
    assert rows[1]["Suggested action"] == "Tune or disable source"
    assert rows[2]["Status"] == "Low evidence"
    assert rows[3]["Status"] == "Healthy"


def test_source_health_action_counts_and_filter_are_shared() -> None:
    """Shared helpers support all dashboard source-health views."""
    rows = [{"Status": "Healthy"}, {"Status": "Low evidence"}, {"Status": "Error"}]

    assert source_health_action("Error", False) == "Fix access or disable source"
    assert source_health_status_counts(rows) == {"Healthy": 1, "Low evidence": 1, "No evidence": 0, "Error": 1}
    assert filter_source_health_rows(rows, "Error") == [{"Status": "Error"}]
    assert filter_source_health_rows(rows, "All statuses") == rows


def test_source_access_limits_note_explains_governed_crawler_boundaries() -> None:
    """Source-health pages should explain blocked-site limits in IT-friendly terms."""
    note = source_access_limits_note()

    assert "Cloudflare" in note
    assert "cookie walls" in note
    assert "proxy/TLS" in note
    assert "does not bypass security controls" in note


def test_source_fallback_candidates_are_limited_to_allowed_error_or_empty_sources() -> None:
    """Fallback candidate planning is explicit and does not include healthy or disallowed sources."""
    run = SimpleNamespace(
        error_summary="Broken Source: timeout",
        sources_snapshot=[
            {"id": 1, "name": "Healthy Source", "url": "https://healthy.example", "organisation": "Org A", "source_type": "FRAMEWORK", "source_role": "PRIMARY_DISCOVERY", "llm_allowed": True},
            {"id": 2, "name": "Broken Source", "url": "https://broken.example", "organisation": "Org B", "source_type": "CATALOGUE", "source_role": "SUPPORTING_DISCOVERY", "llm_allowed": True},
            {"id": 3, "name": "Empty Source", "url": "https://empty.example", "organisation": "Org C", "source_type": "TREND", "source_role": "TREND_VALIDATION", "llm_allowed": True},
            {"id": 4, "name": "Disallowed Empty", "url": "https://no.example", "organisation": "Org D", "source_type": "INDEX", "source_role": "PRIMARY_DISCOVERY", "llm_allowed": False},
        ],
    )
    evidence = [
        Evidence(index, 9, 1, "EXPLICIT_COMPETENCY", f"Evidence {index}", None, "Org A", f"https://healthy.example/{index}", "text", datetime.now())
        for index in range(1, 6)
    ]

    candidates = source_fallback_candidates(run, evidence, {})

    assert [row["Source"] for row in candidates] == ["Broken Source", "Empty Source"]
    assert candidates[0]["Status"] == "Error"
    assert candidates[0]["Fallback intent"] == "Recover STE courses, programmes, certifications, or training resources"
    assert candidates[0]["Recovery readiness"] == "Needs access review"
    assert candidates[0]["Recommended next step"] == "Check network, robots, cookies, proxy, or source URL access before attempting fallback recovery."
    assert candidates[1]["Status"] == "No evidence"
    assert candidates[1]["Fallback intent"] == "Recover STE trend or outlier signals as supporting evidence only"
    assert candidates[1]["Recovery readiness"] == "Optional signal recovery"
    assert candidates[1]["Recommended next step"] == "Run fallback only if officers need extra trend or outlier signals from this source."


def test_fallback_prompt_preview_is_json_safe_and_governed() -> None:
    """Fallback preview defines the future request without calling an LLM."""
    candidate = {
        "Status": "No evidence",
        "Organisation": "Org B",
        "Source": "Org B Catalogue",
        "Source URL": "https://b.example/catalogue",
        "Source family": "HIGHER_LEARNING",
        "Source type": "CATALOGUE",
        "Source role": "SUPPORTING_DISCOVERY",
        "Country": "Singapore",
        "Evidence items": 0,
        "Fallback intent": "Recover STE courses, programmes, certifications, or training resources",
        "Recovery readiness": "Ready for prompt review",
        "Readiness reason": "The source has a structured intent and no retained evidence, so a controlled fallback prompt can be reviewed.",
        "Recommended next step": "Review the fallback prompt preview, then decide whether to run a controlled LLM recovery pass.",
        "Reason": "Crawler produced no retained evidence",
    }

    payload = fallback_prompt_payload(candidate)
    markdown = fallback_prompt_markdown(candidate)

    assert payload["mode"] == "llm_fallback_recovery_preview"
    assert payload["source"]["url"] == "https://b.example/catalogue"
    assert payload["scan_health"]["recovery_readiness"] == "Ready for prompt review"
    assert payload["scan_health"]["recommended_next_step"] == "Review the fallback prompt preview, then decide whether to run a controlled LLM recovery pass."
    assert payload["recovery_objective"] == "Recover STE courses, programmes, certifications, or training resources"
    assert any("Do not invent source URLs" in constraint for constraint in payload["constraints"])
    assert payload["expected_output"]["recovered_items"][0]["evidence_class"] == "competency_or_standard | course_programme_or_resource | research_or_capability | signal_or_topic"
    assert payload["expected_output"]["source_maintenance_advice"]["recommended_replacement_urls"] == ["https://official.example/better-source"]
    assert "This is a preview only" in markdown
    assert "Recovery readiness: Ready for prompt review" in markdown
    assert "Recommended next step: Review the fallback prompt preview" in markdown
    assert "## Expected JSON output shape" in markdown


def test_fallback_readiness_counts_are_stable_for_ui_metrics() -> None:
    """Fallback readiness counts drive compact metrics above candidate tables."""
    counts = fallback_readiness_counts(
        [
            {"Recovery readiness": "Ready for prompt review"},
            {"Recovery readiness": "Ready for prompt review"},
            {"Recovery readiness": "Needs access review"},
            {"Recovery readiness": "Optional signal recovery"},
            {"Recovery readiness": "Something new"},
        ]
    )

    assert counts == {
        "Ready for prompt review": 2,
        "Needs access review": 1,
        "Optional signal recovery": 1,
        "Review manually first": 0,
        "Needs source URL": 0,
    }


def test_filter_fallback_candidates_preserves_default_and_filters_readiness() -> None:
    """Fallback candidate tables can be narrowed by readiness label."""
    rows = [
        {"Recovery readiness": "Ready for prompt review", "Source": "A"},
        {"Recovery readiness": "Needs access review", "Source": "B"},
    ]

    assert filter_fallback_candidates(rows, "All readiness levels") == rows
    assert filter_fallback_candidates(rows, "Needs access review") == [{"Recovery readiness": "Needs access review", "Source": "B"}]


def test_fallback_readiness_filter_options_keep_officer_friendly_order() -> None:
    """Dashboard readiness filters should present the useful review order consistently."""
    assert FALLBACK_READINESS_FILTER_OPTIONS == [
        "All readiness levels",
        "Ready for prompt review",
        "Needs access review",
        "Optional signal recovery",
        "Review manually first",
        "Needs source URL",
    ]


def test_source_maintenance_recommendations_are_review_only() -> None:
    """Source maintenance suggestions should guide catalogue tuning without applying changes."""
    rows = [
        {
            "Status": "Healthy",
            "Evidence items": 10,
            "Organisation": "Org A",
            "Source": "Healthy",
            "Source URL": "https://a.example",
            "LLM fallback allowed": "Yes",
        },
        {
            "Status": "Error",
            "Evidence items": 0,
            "Organisation": "Org B",
            "Source": "Blocked",
            "Source URL": "https://b.example",
            "Source type": "CATALOGUE",
            "Source role": "SUPPORTING_DISCOVERY",
            "Source family": "PROFESSIONAL_BODY",
            "Country": "UK",
            "Reason": "Crawler error or access issue",
            "LLM fallback allowed": "Yes",
            "Suggested action": "Consider LLM fallback",
        },
        {
            "Status": "Low evidence",
            "Evidence items": 2,
            "Organisation": "Org C",
            "Source": "Thin framework",
            "Source URL": "https://c.example/framework",
            "Source type": "FRAMEWORK",
            "LLM fallback allowed": "No",
            "Suggested action": "Review source URL or article limits",
        },
    ]

    recommendations = source_maintenance_recommendations(rows)

    assert [row["Source"] for row in recommendations] == ["Blocked", "Thin framework"]
    assert recommendations[0]["Recommendation type"] == "Access or source URL review"
    assert recommendations[0]["Requires officer approval"] == "Yes"
    assert recommendations[0]["Provenance"] == "Deterministic source-health rule"
    assert recommendations[1]["Recommendation type"] == "Improve configured source URL"


def test_fallback_source_maintenance_recommendations_extract_llm_url_advice() -> None:
    """Saved fallback recovery advice should become source-maintenance rows for officer review."""
    recovery = SimpleNamespace(
        organisation="Org D",
        source_name="Org D Old Catalogue",
        source_url="https://d.example/old",
        recovered_item_count=2,
        raw_result=json.dumps(
            {
                "source_maintenance_advice": {
                    "recommendation_type": "REPLACE_SOURCE_URL",
                    "recommended_replacement_urls": ["https://d.example/new-catalogue"],
                    "reason": "The new catalogue is a more direct official skills source.",
                    "confidence": 0.86,
                }
            }
        ),
    )

    rows = fallback_source_maintenance_recommendations([recovery])

    assert rows[0]["Priority"] == "High"
    assert rows[0]["Recommendation type"] == "Replace Source URL"
    assert rows[0]["Organisation"] == "Org D"
    assert rows[0]["Current URL"] == "https://d.example/old"
    assert rows[0]["Advice confidence"] == "86%"
    assert rows[0]["Recommended replacement URLs"] == "https://d.example/new-catalogue"
    assert rows[0]["Requires officer approval"] == "Yes"
    assert rows[0]["Provenance"] == "LLM-assisted fallback source advice"


def test_fallback_source_maintenance_recommendations_skip_non_actionable_advice() -> None:
    """Keep-current and no-clear-advice results should not clutter source-maintenance tables."""
    recoveries = [
        SimpleNamespace(
            raw_result=json.dumps(
                {
                    "source_maintenance_advice": {
                        "recommendation_type": "KEEP_CURRENT_SOURCE",
                        "recommended_replacement_urls": [],
                        "reason": "The source is still suitable.",
                        "confidence": 0.8,
                    }
                }
            )
        ),
        SimpleNamespace(raw_result="not json"),
    ]

    assert fallback_source_maintenance_recommendations(recoveries) == []


def test_combined_source_maintenance_recommendations_merge_deterministic_and_llm_advice() -> None:
    """Current and historical pages can show one consolidated source-maintenance view."""
    health_rows = [
        {
            "Status": "No evidence",
            "Evidence items": 0,
            "Organisation": "Org E",
            "Source": "Org E Framework",
            "Source URL": "https://e.example/framework",
            "LLM fallback allowed": "No",
            "Suggested action": "Tune or disable source",
        }
    ]
    recoveries = [
        SimpleNamespace(
            organisation="Org F",
            source_name="Org F Hub",
            source_url="https://f.example/hub",
            recovered_item_count=1,
            raw_result=json.dumps(
                {
                    "source_maintenance_advice": {
                        "recommendation_type": "USE_PDF_OR_RESOURCE_HUB",
                        "recommended_replacement_urls": ["https://f.example/resources"],
                        "reason": "The resource hub is more structured.",
                        "confidence": 0.7,
                    }
                }
            ),
        )
    ]

    rows = combined_source_maintenance_recommendations(health_rows, recoveries)

    assert [row["Provenance"] for row in rows] == ["Deterministic source-health rule", "LLM-assisted fallback source advice"]
    assert rows[0]["Recommended replacement URLs"] == ""
    assert rows[1]["Recommendation type"] == "Use PDF Or Resource Hub"


def test_source_maintenance_priority_counts_are_stable_for_ui_metrics() -> None:
    """Source-maintenance dashboards should show compact priority totals."""
    counts = source_maintenance_priority_counts(
        [
            {"Priority": "High"},
            {"Priority": "High"},
            {"Priority": "Medium"},
            {"Priority": "Unknown"},
            {},
        ]
    )

    assert counts == {"High": 2, "Medium": 1, "Low": 1}


def test_automatic_fallback_queue_only_selects_bounded_ready_candidates() -> None:
    """Automatic recovery planning must not bypass access or manual-review gates."""
    candidates = [
        {"Source": "Ready 1", "Recovery readiness": FALLBACK_READINESS_READY},
        {"Source": "Blocked", "Recovery readiness": "Needs access review"},
        {"Source": "Ready 2", "Recovery readiness": FALLBACK_READINESS_READY},
        {"Source": "Ready 3", "Recovery readiness": FALLBACK_READINESS_READY},
    ]
    queued = automatic_fallback_queue(candidates, limit=2)
    assert [row["Source"] for row in queued] == ["Ready 1", "Ready 2"]
    assert all(row["Queue status"] == "Eligible for governed automatic recovery" for row in queued)


def test_replacement_url_prompt_locks_organisation_and_requires_official_urls() -> None:
    """The future URL-advice call must preserve provenance and organisation identity."""
    payload = replacement_url_prompt_payload({
        "Organisation": "NUS",
        "Source": "NUS News",
        "Current URL": "https://news.nus.edu.sg/news-reports",
        "Source family": "HIGHER_LEARNING",
        "Source type": "ARTICLE",
        "Country": "Singapore",
        "Crawler issue": "No evidence",
    })
    assert payload["mode"] == "source_url_recommendation"
    assert payload["organisation"] == "NUS"
    assert payload["current_source"]["url"] == "https://news.nus.edu.sg/news-reports"
    assert "Do not invent URLs and do not recommend a different organisation." in payload["fixed_instructions"]
    assert "AI replacement URL recommendation preview" in replacement_url_prompt_markdown(payload["current_source"] | {"Organisation": "NUS", "Source": "NUS News"})


def test_source_type_inference_handles_common_catalogue_and_framework_paths() -> None:
    assert infer_source_type_from_url("https://example.org/competency-framework") == "FRAMEWORK"
    assert infer_source_type_from_url("https://example.org/programmes/courses") == "CATALOGUE"
    assert infer_source_type_from_url("https://example.org/research/publications") == "INDEX"
    assert infer_source_type_from_url("https://example.org/news/insights") == "TREND"
