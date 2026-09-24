from datetime import datetime
import json
from types import SimpleNamespace

from src.dashboard.recommendations import _recommendation_summary_csv
from src.dashboard.scan_report import _enrich_organised_scan, _filter_source_health_rows, _organised_scan_rows, _organised_scan_sample_rows, _serialise_batch, _source_health_action, _source_health_rows, _source_health_status_counts
from src.models.domain import Evidence, ScanStatus, Source, SourceFamily, SourceRole, SourceType


def test_organised_scan_rows_sort_by_total_evidence_and_show_bucket_counts() -> None:
    """History page exposes the organised scan as a compact officer-facing table."""
    organised_scan = {
        "organisations": [
            {
                "organisation": "Org B",
                "counts": {
                    "competencies_or_standards": 1,
                    "courses_programmes_or_resources": 0,
                    "research_reports_or_capability": 0,
                    "signals_and_topics": 1,
                },
            },
            {
                "organisation": "Org A",
                "counts": {
                    "competencies_or_standards": 2,
                    "courses_programmes_or_resources": 1,
                    "research_reports_or_capability": 1,
                    "signals_and_topics": 0,
                },
            },
        ]
    }

    rows = _organised_scan_rows(organised_scan)

    assert rows[0]["Organisation"] == "Org A"
    assert rows[0]["Competencies / standards"] == 2
    assert rows[0]["Courses / resources"] == 1
    assert rows[0]["Research / capability"] == 1
    assert rows[0]["Signals / topics"] == 0
    assert rows[0]["Total"] == 4


def test_organised_scan_sample_rows_show_representative_item_details() -> None:
    """Representative organised items include links and snippets for quick officer review."""
    organisation_payload = {
        "competencies_or_standards": [
            {
                "id": 8,
                "title": "Competency framework",
                "url": "https://example.org/framework",
                "evidence_type": "EXPLICIT_COMPETENCY",
                "explicit_or_inferred": "EXPLICIT",
                "snippet": "Defines capability expectations.",
            }
        ]
    }

    rows = _organised_scan_sample_rows(organisation_payload, "competencies_or_standards")

    assert rows == [
        {
            "Evidence ID": 8,
            "Title": "Competency framework",
            "Evidence type": "explicit competency",
            "Evidence state": "EXPLICIT",
            "URL": "https://example.org/framework",
            "Snippet": "Defines capability expectations.",
        }
    ]


def test_enriched_organised_scan_export_includes_source_metadata() -> None:
    """Downloaded organised scan JSON carries source provenance metadata for audit."""
    evidence = [
        Evidence(8, 1, 3, "EXPLICIT_COMPETENCY", "Competency framework", None, "Org A", "https://example.org/framework", "Text", datetime.now())
    ]
    source_lookup = {
        3: Source(
            3,
            "Org A framework",
            "https://example.org/framework",
            "Org A",
            country="Singapore",
            source_family=SourceFamily.GOVERNMENT_AGENCY,
            source_type=SourceType.FRAMEWORK,
            source_role=SourceRole.PRIMARY_DISCOVERY,
        )
    }
    organised_scan = {
        "organisations": [
            {
                "organisation": "Org A",
                "counts": {"competencies_or_standards": 1},
                "competencies_or_standards": [{"id": 8, "title": "Competency framework"}],
            }
        ]
    }

    enriched = _enrich_organised_scan(organised_scan, evidence, source_lookup)
    organisation = enriched["organisations"][0]
    item = organisation["competencies_or_standards"][0]

    assert organisation["source_metadata"]["countries"] == ["Singapore"]
    assert organisation["source_metadata"]["source_families"] == ["GOVERNMENT_AGENCY"]
    assert item["source_metadata"]["source_type"] == "FRAMEWORK"
    assert item["source_metadata"]["source_role"] == "PRIMARY_DISCOVERY"


def test_source_health_rows_include_sources_with_no_evidence_and_errors() -> None:
    """History source health should show configured sources even when they stored no evidence."""
    run = SimpleNamespace(
        error_summary="GovTech Media: No permitted article links discovered",
        sources_snapshot=[
            {
                "id": 1,
                "name": "Strong Source",
                "organisation": "Org A",
                "source_family": "PROFESSIONAL_BODY",
                "source_type": "FRAMEWORK",
                "source_role": "PRIMARY_DISCOVERY",
                "llm_allowed": True,
            },
            {
                "id": 2,
                "name": "GovTech Media",
                "organisation": "GovTech",
                "source_family": "GOVERNMENT_AGENCY",
                "source_type": "TREND",
                "source_role": "TREND_VALIDATION",
                "llm_allowed": True,
            },
            {
                "name": "Quiet Source",
                "url": "https://quiet.example",
                "organisation": "Org C",
                "source_family": "HIGHER_LEARNING",
                "source_type": "CATALOGUE",
                "source_role": "SUPPORTING_DISCOVERY",
                "llm_allowed": False,
            },
            {
                "id": 4,
                "name": "Empty Source",
                "organisation": "Org D",
                "source_family": "PROFESSIONAL_BODY",
                "source_type": "FRAMEWORK",
                "source_role": "PRIMARY_DISCOVERY",
                "llm_allowed": True,
            },
        ],
    )
    evidence = [
        Evidence(1, 1, 1, "EXPLICIT_COMPETENCY", "A", None, "Org A", "https://a.example/1", "text", datetime.now()),
        Evidence(2, 1, 1, "EXPLICIT_COMPETENCY", "B", None, "Org A", "https://a.example/2", "text", datetime.now()),
        Evidence(3, 1, 1, "EXPLICIT_COMPETENCY", "C", None, "Org A", "https://a.example/3", "text", datetime.now()),
        Evidence(4, 1, 1, "EXPLICIT_COMPETENCY", "D", None, "Org A", "https://a.example/4", "text", datetime.now()),
        Evidence(5, 1, 1, "EXPLICIT_COMPETENCY", "E", None, "Org A", "https://a.example/5", "text", datetime.now()),
        Evidence(6, 1, 3, "COURSE", "Quiet course", None, "Org C", "https://quiet.example/course", "text", datetime.now()),
    ]
    source_lookup = {
        3: Source(3, "Quiet Source", "https://quiet.example", "Org C", source_family=SourceFamily.HIGHER_LEARNING),
    }

    rows = _source_health_rows(run, evidence, source_lookup)

    assert rows[0]["Source"] == "GovTech Media"
    assert rows[0]["Status"] == "Error"
    assert rows[0]["Suggested action"] == "Consider LLM fallback"
    assert rows[1]["Source"] == "Empty Source"
    assert rows[1]["Status"] == "No evidence"
    assert rows[1]["Suggested action"] == "Consider LLM fallback"
    assert rows[2]["Source"] == "Quiet Source"
    assert rows[2]["Status"] == "Low evidence"
    assert rows[2]["Evidence items"] == 1
    assert rows[2]["Suggested action"] == "Review source URL or article limits"
    assert rows[3]["Source"] == "Strong Source"
    assert rows[3]["Status"] == "Healthy"
    assert rows[3]["Evidence items"] == 5
    assert rows[3]["Suggested action"] == "Keep current crawler"


def test_source_health_rows_can_be_exported_as_csv() -> None:
    """Source health rows should be spreadsheet-friendly for source tuning reviews."""
    rows = [
        {
            "Status": "Low evidence",
            "Evidence items": 2,
            "Source family": "🟢 professional body",
            "Source type": "🟢 framework",
            "Source role": "🟦 primary",
            "Organisation": "Org A",
            "Source": "Org A Framework",
            "LLM fallback allowed": "Yes",
            "Suggested action": "Review source URL or article limits",
        }
    ]

    csv_text = _recommendation_summary_csv(rows)

    assert csv_text.splitlines()[0] == "Status,Evidence items,Source family,Source type,Source role,Organisation,Source,LLM fallback allowed,Suggested action"
    assert "Low evidence,2,🟢 professional body,🟢 framework,🟦 primary,Org A,Org A Framework,Yes,Review source URL or article limits" in csv_text


def test_source_health_action_respects_fallback_permission() -> None:
    """Action suggestions should not recommend LLM fallback when the source disallows it."""
    assert _source_health_action("No evidence", True) == "Consider LLM fallback"
    assert _source_health_action("No evidence", False) == "Tune or disable source"
    assert _source_health_action("Error", False) == "Fix access or disable source"


def test_source_health_status_counts_support_summary_metrics() -> None:
    """Source health status counts drive the compact metrics above the table."""
    counts = _source_health_status_counts(
        [
            {"Status": "Healthy"},
            {"Status": "Healthy"},
            {"Status": "Low evidence"},
            {"Status": "No evidence"},
            {"Status": "Error"},
        ]
    )

    assert counts == {"Healthy": 2, "Low evidence": 1, "No evidence": 1, "Error": 1}


def test_filter_source_health_rows_preserves_default_and_filters_status() -> None:
    """Source-health table can be narrowed to problematic sources."""
    rows = [
        {"Status": "Healthy", "Source": "A"},
        {"Status": "Error", "Source": "B"},
        {"Status": "No evidence", "Source": "C"},
    ]

    assert _filter_source_health_rows(rows, "All statuses") == rows
    assert _filter_source_health_rows(rows, "Error") == [{"Status": "Error", "Source": "B"}]


def test_batch_json_export_includes_source_health_summary() -> None:
    """Downloaded batch evidence JSON should include source-health triage metadata."""
    run = SimpleNamespace(
        id=7,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        status=ScanStatus.COMPLETED,
        error_summary=None,
        sources_snapshot=[
            {
                "id": 3,
                "name": "Org A Framework",
                "url": "https://a.example/framework",
                "organisation": "Org A",
                "source_family": "PROFESSIONAL_BODY",
                "source_type": "FRAMEWORK",
                "source_role": "PRIMARY_DISCOVERY",
                "llm_allowed": True,
            },
            {
                "id": 4,
                "name": "Org B Catalogue",
                "url": "https://b.example/catalogue",
                "organisation": "Org B",
                "source_family": "HIGHER_LEARNING",
                "source_type": "CATALOGUE",
                "source_role": "SUPPORTING_DISCOVERY",
                "llm_allowed": True,
            }
        ],
    )
    evidence = [
        Evidence(1, 7, 3, "EXPLICIT_COMPETENCY", "Framework", None, "Org A", "https://a.example/framework", "text", datetime.now())
    ]
    source_lookup = {
        3: Source(3, "Org A Framework", "https://a.example/framework", "Org A", source_family=SourceFamily.PROFESSIONAL_BODY)
    }

    fallback_recoveries = [
        SimpleNamespace(
            id=12,
            scan_run_id=7,
            source_name="Org B Catalogue",
            organisation="Org B",
            source_url="https://b.example/catalogue",
            recovery_status="COMPLETED",
            recovered_item_count=1,
            raw_result=json.dumps({"recovered_items": [{"title": "Recovered resource"}]}),
            created_at=datetime.now(),
        )
    ]

    payload = json.loads(_serialise_batch(run, evidence, None, [], None, source_lookup, fallback_recoveries))
    health_by_source = {row["Source"]: row for row in payload["source_health"]}

    assert payload["source_health_counts"] == {"Healthy": 0, "Low evidence": 1, "No evidence": 1, "Error": 0}
    assert health_by_source["Org A Framework"]["Suggested action"] == "Review source URL or article limits"
    assert health_by_source["Org B Catalogue"]["Suggested action"] == "Consider LLM fallback"
    assert payload["source_maintenance_recommendations"][0]["Source"] == "Org B Catalogue"
    assert payload["source_maintenance_recommendations"][0]["Recommendation type"] == "Fallback or replacement URL review"
    assert payload["source_maintenance_recommendations"][0]["Requires officer approval"] == "Yes"
    assert payload["source_maintenance_priority_counts"] == {"High": 1, "Medium": 1, "Low": 0}
    assert payload["llm_fallback_candidates"][0]["Source"] == "Org B Catalogue"
    assert payload["llm_fallback_candidates"][0]["Fallback intent"] == "Recover STE courses, programmes, certifications, or training resources"
    assert payload["llm_fallback_readiness_counts"]["Ready for prompt review"] == 1
    assert payload["llm_fallback_request_preview"][0]["source"]["url"] == "https://b.example/catalogue"
    assert payload["llm_fallback_request_preview"][0]["source"]["source_type"] == "CATALOGUE"
    assert payload["llm_fallback_request_preview"][0]["mode"] == "llm_fallback_recovery_preview"
    assert payload["llm_fallback_recoveries"][0]["source_name"] == "Org B Catalogue"
    assert payload["llm_fallback_recoveries"][0]["result"]["recovered_items"][0]["title"] == "Recovered resource"
