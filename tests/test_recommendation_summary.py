from datetime import datetime
import json
from types import SimpleNamespace

from src.dashboard.recommendations import ASK_AI_QUESTION_STARTERS, ASK_AI_RECENT_QA_LIMIT, _build_question_context, _build_recommendation_pack, _current_source_health_rows, _fallback_recovery_summary_rows, _filter_source_health_rows, _human_label, _question_history_csv, _question_history_markdown, _question_history_summary, _recommendation_pack_markdown, _recommendation_summary_csv, _recommendation_summary_rows, _source_role_badge, _source_type_badge, _support_coverage_rows
from src.models.domain import Evidence, FrameworkVersion, Recommendation, Source, SourceFamily


class _QuestionRow(dict):
    """Tiny sqlite.Row-like helper for export tests."""

    def __getitem__(self, key):
        return dict.__getitem__(self, key)


def test_human_label_formats_enum_style_values() -> None:
    """Recommendation and source enum labels are readable in officer-facing UI/export text."""
    assert _human_label("NEW_SUB_FUNCTIONAL_AREA").title() == "New Sub Functional Area"


def test_ask_ai_question_starters_cover_batch_review_use_cases() -> None:
    """Starter prompts should help officers use the batch-grounded Ask AI panel."""
    joined = " ".join(ASK_AI_QUESTION_STARTERS).lower()

    assert "outlier signal" in joined
    assert "trend/news signals" in joined
    assert "new ste sub-functional areas" in joined


def test_current_source_health_rows_support_current_recommendation_pack_export() -> None:
    """Current recommendation packs include source-health rows using scan snapshot metadata."""
    run = SimpleNamespace(
        error_summary="",
        sources_snapshot=[
            {
                "name": "Org A Framework",
                "url": "https://a.example",
                "organisation": "Org A",
                "source_family": "PROFESSIONAL_BODY",
                "source_type": "FRAMEWORK",
                "source_role": "PRIMARY_DISCOVERY",
                "llm_allowed": True,
            }
        ],
    )
    evidence = [Evidence(1, 7, 10, "EXPLICIT_COMPETENCY", "A", None, "Org A", "https://a.example/page", "text", datetime.now())]
    source_lookup = {
        10: Source(10, "Org A Framework", "https://a.example", "Org A", source_family=SourceFamily.PROFESSIONAL_BODY),
    }

    rows = _current_source_health_rows(run, evidence, source_lookup)

    assert rows[0]["Source"] == "Org A Framework"
    assert rows[0]["Status"] == "Low evidence"
    assert rows[0]["Suggested action"] == "Review source URL or article limits"


def test_fallback_recovery_summary_rows_are_officer_readable() -> None:
    """Current Recommendations can show saved fallback recoveries compactly."""
    rows = _fallback_recovery_summary_rows(
        [
            SimpleNamespace(
                id=2,
                created_at=datetime.fromisoformat("2026-08-27T12:30:00"),
                recovery_status="COMPLETED",
                organisation="Org A",
                source_name="Org A Catalogue",
                recovered_item_count=3,
                source_url="https://a.example/catalogue",
            )
        ]
    )

    assert rows == [
        {
            "Record ID": 2,
            "Created": "2026-08-27 12:30",
            "Status": "Completed",
            "Provenance": "🤖 LLM assisted",
            "Verification": "🟡 Needs verification",
            "Organisation": "Org A",
            "Source": "Org A Catalogue",
            "Recovered items": 3,
            "Source advice": "No advice recorded",
            "Source URL": "https://a.example/catalogue",
        }
    ]


def test_current_source_health_filter_preserves_default_and_filters_status() -> None:
    """Current Recommendations can narrow source-health rows to problem statuses."""
    rows = [
        {"Status": "Healthy", "Source": "A"},
        {"Status": "Error", "Source": "B"},
    ]

    assert _filter_source_health_rows(rows, "All statuses") == rows
    assert _filter_source_health_rows(rows, "Error") == [{"Status": "Error", "Source": "B"}]


def test_source_badges_include_human_readable_labels() -> None:
    """Source badges should not expose raw backend enum labels in officer-facing UI."""
    assert _source_type_badge("FRAMEWORK") == "🟢 framework"
    assert _source_role_badge("PRIMARY_DISCOVERY") == "🟦 primary"


def test_recommendation_summary_rows_show_support_strength() -> None:
    """Officer summary rows expose evidence, organisation and source-family counts."""
    recommendation = Recommendation(
        1,
        1,
        "NEW_COMPETENCY",
        0.91,
        "Reasoning",
        "Urban Planning",
        "Digital Twins",
        "Add competency",
        "Reasons",
        (1, 2, 3),
        (),
        (),
    )
    evidence_by_id = {
        1: Evidence(1, 1, 10, "ARTICLE_TEXT", "A", None, "Org A", "https://a.example", "text", datetime.now()),
        2: Evidence(2, 1, 11, "EXPLICIT_COMPETENCY", "B", None, "Org B", "https://b.example", "text", datetime.now()),
        3: Evidence(3, 1, 11, "EXPLICIT_COMPETENCY", "C", None, "Org B", "https://c.example", "text", datetime.now()),
    }
    source_lookup = {
        10: Source(10, "A", "https://a.example", "Org A", source_family=SourceFamily.GOVERNMENT_AGENCY),
        11: Source(11, "B", "https://b.example", "Org B", source_family=SourceFamily.PROFESSIONAL_BODY),
    }

    row = _recommendation_summary_rows([recommendation], evidence_by_id, source_lookup)[0]

    assert row["Supporting sources"] == 3
    assert row["Supporting organisations"] == 2
    assert row["Source family types"] == 2
    assert row["Confidence"] == "91%"


def test_support_coverage_rows_count_families_and_organisations() -> None:
    """Support coverage helps officers spot concentration by source family or organisation."""
    recommendation = Recommendation(
        1,
        1,
        "NEW_COMPETENCY",
        0.91,
        "Reasoning",
        "Urban Planning",
        "Digital Twins",
        "Add competency",
        "Reasons",
        (1, 2),
        (),
        (),
    )
    evidence_by_id = {
        1: Evidence(1, 1, 10, "ARTICLE_TEXT", "A", None, "Org A", "https://a.example", "text", datetime.now()),
        2: Evidence(2, 1, 11, "EXPLICIT_COMPETENCY", "B", None, "Org B", "https://b.example", "text", datetime.now()),
    }
    source_lookup = {
        10: Source(10, "A", "https://a.example", "Org A", source_family=SourceFamily.GOVERNMENT_AGENCY),
        11: Source(11, "B", "https://b.example", "Org B", source_family=SourceFamily.PROFESSIONAL_BODY),
    }

    family_rows, organisation_rows = _support_coverage_rows([recommendation], evidence_by_id, source_lookup)

    assert family_rows == [
        {"Source family": "Government Agency", "Cited evidence count": 1},
        {"Source family": "Professional Body", "Cited evidence count": 1},
    ]
    assert organisation_rows == [
        {"Organisation": "Org A", "Cited evidence count": 1},
        {"Organisation": "Org B", "Cited evidence count": 1},
    ]


def test_recommendation_summary_rows_fall_back_to_stored_provenance() -> None:
    """Summary rows still show source strength when full evidence text is no longer loaded."""
    recommendation = Recommendation(
        1,
        1,
        "NEW_COMPETENCY",
        0.82,
        "Reasoning",
        "Infrastructure",
        "Accessible Design",
        "Add competency",
        "Reasons",
        (10, 11, 12),
        ("https://a.example", "https://b.example", "https://b.example"),
        ("Org A", "Org B", "Org B"),
    )
    source_lookup = {
        10: Source(10, "A", "https://a.example", "Org A", source_family=SourceFamily.GOVERNMENT_AGENCY),
        11: Source(11, "B", "https://b.example", "Org B", source_family=SourceFamily.PROFESSIONAL_BODY),
    }

    row = _recommendation_summary_rows([recommendation], {}, source_lookup)[0]

    assert row["Supporting sources"] == 2
    assert row["Supporting organisations"] == 2
    assert row["Source family types"] == 2


def test_recommendation_summary_rows_mark_family_unavailable_when_catalogue_cannot_match() -> None:
    """Family counts are explicit when stored organisations cannot be matched to configured sources."""
    recommendation = Recommendation(
        1,
        1,
        "NEW_COMPETENCY",
        0.82,
        "Reasoning",
        "Infrastructure",
        "Accessible Design",
        "Add competency",
        "Reasons",
        (10, 11),
        ("https://a.example", "https://b.example"),
        ("Archived Org A", "Archived Org B"),
    )

    row = _recommendation_summary_rows([recommendation], {}, {})[0]

    assert row["Supporting sources"] == 2
    assert row["Supporting organisations"] == 2
    assert row["Source family types"] == "Unavailable"


def test_question_context_includes_recommendation_summary_and_support_profile() -> None:
    """The follow-up question LLM receives the same support metadata shown to officers."""
    evidence = [
        Evidence(1, 7, 10, "ARTICLE_TEXT", "A", None, "Org A", "https://a.example", "evidence text", datetime.now()),
        Evidence(2, 7, 11, "EXPLICIT_COMPETENCY", "B", None, "Org B", "https://b.example", "more evidence", datetime.now()),
    ]
    recommendation = Recommendation(
        1,
        1,
        "NEW_SUB_FUNCTIONAL_AREA",
        0.9,
        "Reasoning",
        "AI Assurance",
        "Trustworthy AI Governance",
        "Add new area",
        "Evidence shows a gap.",
        (1, 2),
        ("https://a.example", "https://b.example"),
        ("Org A", "Org B"),
    )
    source_lookup = {
        10: Source(10, "A", "https://a.example", "Org A", source_family=SourceFamily.GOVERNMENT_AGENCY),
        11: Source(11, "B", "https://b.example", "Org B", source_family=SourceFamily.PROFESSIONAL_BODY),
    }

    source_health = [
        {
            "Status": "Low evidence",
            "Evidence items": 2,
            "Organisation": "Org A",
            "Source": "A",
            "Suggested action": "Review source URL or article limits",
        }
    ]

    fallback_candidates = [
        {
            "Status": "No evidence",
            "Organisation": "Org C",
                "Source": "Org C Catalogue",
                "Source URL": "https://c.example/catalogue",
                "Source type": "CATALOGUE",
                "Source role": "SUPPORTING_DISCOVERY",
                "Fallback intent": "Recover STE courses, programmes, certifications, or training resources",
                "Recovery readiness": "Ready for prompt review",
                "Recommended next step": "Review the fallback prompt preview, then decide whether to run a controlled LLM recovery pass.",
            }
        ]

    fallback_recoveries = [
        SimpleNamespace(
            id=5,
            scan_run_id=7,
            source_name="Org C Catalogue",
            organisation="Org C",
            source_url="https://c.example/catalogue",
            recovery_status="COMPLETED",
            recovered_item_count=1,
            raw_result=json.dumps({"recovered_items": [{"title": "Recovered course"}]}),
            created_at=datetime.fromisoformat("2026-08-26T10:00:00"),
        )
    ]

    context = _build_question_context(7, None, {"framework": "snapshot"}, evidence, [recommendation], source_lookup, source_health, fallback_candidates, fallback_recoveries)

    assert context["scan_batch"]["id"] == 7
    assert context["organised_scan_quality"]["label"] == "Mixed"
    assert context["organised_scan_quality"]["primary_evidence_items"] == 1
    assert context["organised_scan_quality"]["signal_evidence_items"] == 1
    assert context["recommendation_summary"][0]["Source family types"] == 2
    assert context["support_coverage"]["source_families"] == [
        {"Source family": "Government Agency", "Cited evidence count": 1},
        {"Source family": "Professional Body", "Cited evidence count": 1},
    ]
    assert context["source_health_counts"] == {"Healthy": 0, "Low evidence": 1, "No evidence": 0, "Error": 0}
    assert context["source_health"][0]["Suggested action"] == "Review source URL or article limits"
    assert context["source_maintenance_recommendations"][0]["Recommendation type"] == "Review article limits or source relevance"
    assert context["source_maintenance_recommendations"][0]["Requires officer approval"] == "Yes"
    assert context["source_maintenance_priority_counts"] == {"High": 0, "Medium": 0, "Low": 1}
    assert context["llm_fallback_candidates"][0]["Source"] == "Org C Catalogue"
    assert context["llm_fallback_readiness_counts"]["Ready for prompt review"] == 1
    assert context["llm_fallback_request_preview"][0]["source"]["url"] == "https://c.example/catalogue"
    assert context["llm_fallback_recoveries"][0]["source_name"] == "Org C Catalogue"
    assert context["llm_fallback_recoveries"][0]["result"]["recovered_items"][0]["title"] == "Recovered course"
    assert context["question_history_policy"]["scope"] == "same recommendation batch only"
    assert context["question_history_summary"]["question_count"] == 0
    assert context["recommendations"][0]["support_profile"]["Supporting sources"] == 2
    assert context["recommendations"][0]["support_summary"] == "2 source(s) · 2 org(s) · 2 source family type(s)"
    assert context["evidence"][0]["article_preview"] == "evidence text"
    assert context["evidence"][0]["article_preview_truncated"] is False
    assert "article_text" not in context["evidence"][0]
    assert context["source_lookup"][10]["source_family"] == "GOVERNMENT_AGENCY"


def test_question_context_includes_bounded_recent_question_history() -> None:
    """Ask AI should have same-batch continuity without unlimited chatbot memory."""
    question_history = [
        _QuestionRow({"id": index, "asked_at": f"2026-08-25T10:0{index}:00", "question": f"Question {index}", "answer": "A" * 1500})
        for index in range(7)
    ]

    context = _build_question_context(7, None, {"framework": "snapshot"}, [], [], {}, question_history=question_history)

    assert len(context["recent_question_history"]) == min(ASK_AI_RECENT_QA_LIMIT, len(question_history))
    assert context["question_history_summary"]["question_count"] == 7
    assert context["recent_question_history"][0]["question"] == "Question 0"
    assert len(context["recent_question_history"][0]["answer"]) == 1000
    assert context["recent_question_history"][0]["answer_preview_truncated"] is True
    assert context["question_history_policy"]["use_as"] == "conversation context only, not source evidence"


def test_question_context_serialises_framework_version_for_json_payload() -> None:
    """Ask AI context must be JSON-safe before it is sent to OpenAI or logged."""
    framework = FrameworkVersion(3, "2026.1", datetime(2026, 8, 25, 9, 30), True)
    selected_batch = {
        "id": 4,
        "framework_version_id": 3,
        "scan_run_id": 7,
        "created_at": "2026-08-25T10:00:00",
        "recommendation_count": 1,
        "framework_snapshot": '{"areas":[{"cap_area":"Digital","sub_functional_area":"AI"}]}',
    }

    context = _build_question_context(7, selected_batch, framework, [], [], {})

    assert context["framework"]["metadata"]["version"] == "2026.1"
    assert context["framework"]["snapshot"]["areas"][0]["cap_area"] == "Digital"
    json.dumps(context)


def test_question_context_uses_compact_evidence_previews() -> None:
    """Ask AI context should stay bounded even when retained evidence text is long."""
    long_text = "A" * 1500
    evidence = [Evidence(1, 7, 10, "ARTICLE_TEXT", "A", None, "Org A", "https://a.example", long_text, datetime.now())]

    recommendation = Recommendation(1, 1, "NEW_COMPETENCY", 0.8, "Reason", "Area", "Skill", "Add", "Gap", (1,), (), ())
    context = _build_question_context(7, None, {"framework": "snapshot"}, evidence, [recommendation], {})

    assert len(context["evidence"][0]["article_preview"]) == 1200
    assert context["evidence"][0]["article_preview_chars"] == 1200
    assert context["evidence"][0]["article_original_chars"] == 1500
    assert context["evidence"][0]["article_preview_truncated"] is True
    assert "article_text" not in context["evidence"][0]


def test_live_question_context_drops_large_diagnostics_without_changing_export():
    from src.dashboard.recommendations import _compact_live_question_context
    original = {'source_health': [{'detail': 'X' * 150000}],
                'source_maintenance_recommendations': [{'detail': 'Y' * 150000}],
                'llm_fallback_recoveries': ['Z' * 150000],
                'source_health_counts': {'Error': 2},
                'framework': {'version': 'test'}, 'evidence': [{'id': 1}],
                'recommendations': [{'id': 2}], 'recent_question_history': []}
    compact = _compact_live_question_context(original)
    assert 'source_health' not in compact
    assert 'source_maintenance_recommendations' not in compact
    assert 'llm_fallback_recoveries' not in compact
    assert compact['source_health_counts'] == {'Error': 2}
    assert compact['evidence'] == [{'id': 1}]
    assert compact['framework'] == {'version': 'test'}
    assert len(json.dumps(compact)) < 1000
    assert 'source_health' in original  # Export data is not mutated.


def test_question_context_excludes_uncited_scan_and_batch_blobs():
    evidence = [Evidence(i, 7, i, "ARTICLE_TEXT", str(i), None, "Org", f"https://example.org/{i}", "X" * 2000, datetime.now()) for i in range(1000)]
    recommendation = Recommendation(1, 1, "NEW_COMPETENCY", 0.8, "Reason", "Area", "Skill", "Add", "Gap", (1, 2000), ("https://example.org/2",), ())
    batch = {"id": 1, "created_at": "2026-09-15T10:00:00", "organised_scan_snapshot": "SECRET_UNCITED" * 10000}
    context = _build_question_context(7, batch, None, evidence, [recommendation], {})
    assert [item['id'] for item in context['evidence']] == [1, 2]
    assert context['evidence_scope']['missing_cited_ids'] == [2000]
    assert 'SECRET_UNCITED' not in json.dumps(context)
    assert len(json.dumps(context)) < 15000
    assert _build_question_context(7, batch, None, evidence, [], {})['evidence'] == []


def test_recommendation_pack_is_compact_and_auditable() -> None:
    """Supervisor export contains recommendation support context without full article text."""
    evidence = [
        Evidence(1, 7, 10, "ARTICLE_TEXT", "A", None, "Org A", "https://a.example", "long article text", datetime.now()),
    ]
    recommendation = Recommendation(
        1,
        1,
        "NEW_COMPETENCY",
        0.88,
        "Reasoning",
        "Systems",
        "Digital Thread",
        "Add competency",
        "Evidence shows a gap.",
        (1,),
        ("https://a.example",),
        ("Org A",),
    )
    source_lookup = {
        10: Source(10, "A", "https://a.example", "Org A", source_family=SourceFamily.GOVERNMENT_AGENCY),
    }
    question_history = [
        _QuestionRow({"id": 5, "asked_at": "2026-08-25T10:30:00", "question": "Why?", "answer": "Because evidence supports it."})
    ]

    source_health = [
        {
            "Status": "Low evidence",
            "Evidence items": 1,
            "Organisation": "Org A",
            "Source": "A",
            "Suggested action": "Review source URL or article limits",
        }
    ]

    fallback_candidates = [
            {
                "Status": "No evidence",
                "Organisation": "Org B",
                "Source": "Org B Catalogue",
                "Source URL": "https://b.example/catalogue",
                "Source type": "CATALOGUE",
                "Source role": "SUPPORTING_DISCOVERY",
                "Fallback intent": "Recover STE courses, programmes, certifications, or training resources",
                "Recovery readiness": "Ready for prompt review",
                "Recommended next step": "Review the fallback prompt preview, then decide whether to run a controlled LLM recovery pass.",
            }
        ]
    fallback_recoveries = [
        SimpleNamespace(
            id=8,
            scan_run_id=7,
            source_name="Org B Catalogue",
            organisation="Org B",
            source_url="https://b.example/catalogue",
            recovery_status="COMPLETED",
            recovered_item_count=2,
            raw_result=json.dumps({"recovered_items": [{"title": "Recovered certification"}]}),
            created_at=datetime.fromisoformat("2026-08-26T11:00:00"),
        )
    ]

    pack = _build_recommendation_pack(7, None, {"framework": "snapshot"}, evidence, [recommendation], source_lookup, question_history, source_health, fallback_candidates, fallback_recoveries)

    assert pack["export_type"] == "recommendation_pack"
    assert pack["recommendation_summary"][0]["Supporting sources"] == 1
    assert pack["organised_scan_quality"]["label"] == "Signal-heavy"
    assert pack["support_coverage"]["source_families"][0]["Source family"] == "Government Agency"
    assert pack["support_coverage"]["organisations"][0]["Organisation"] == "Org A"
    assert pack["source_health_counts"] == {"Healthy": 0, "Low evidence": 1, "No evidence": 0, "Error": 0}
    assert pack["source_health"][0]["Suggested action"] == "Review source URL or article limits"
    assert pack["source_maintenance_recommendations"][0]["Recommendation type"] == "Review article limits or source relevance"
    assert pack["source_maintenance_recommendations"][0]["Provenance"] == "Deterministic source-health rule"
    assert pack["source_maintenance_priority_counts"] == {"High": 0, "Medium": 0, "Low": 1}
    assert pack["llm_fallback_candidates"][0]["Source"] == "Org B Catalogue"
    assert pack["llm_fallback_readiness_counts"]["Ready for prompt review"] == 1
    assert pack["llm_fallback_request_preview"][0]["source"]["source_type"] == "CATALOGUE"
    assert pack["llm_fallback_recoveries"][0]["recovered_item_count"] == 2
    assert pack["llm_fallback_recoveries"][0]["provenance"] == "🤖 LLM assisted"
    assert pack["llm_fallback_recoveries"][0]["verification_status"] == "🟡 Needs verification"
    assert pack["llm_fallback_recoveries"][0]["result"]["recovered_items"][0]["title"] == "Recovered certification"
    assert pack["recommendations"][0]["support_profile"]["Supporting organisations"] == 1
    assert pack["cited_evidence"][0]["url"] == "https://a.example"
    assert "article_text" not in pack["cited_evidence"][0]
    assert pack["source_lookup"][10]["source_family"] == "GOVERNMENT_AGENCY"
    assert pack["recommendations"][0]["supporting_sources"][0]["evidence_id"] == 1
    assert pack["recommendations"][0]["supporting_sources"][0]["title"] == "A"
    assert pack["recommendations"][0]["supporting_sources"][0]["source_family"] == "GOVERNMENT_AGENCY"
    assert pack["saved_questions"][0]["question"] == "Why?"
    assert pack["question_history_summary"]["question_count"] == 1
    json.dumps(pack)


def test_recommendation_pack_markdown_is_human_readable() -> None:
    """Markdown export gives supervisors a readable pack without opening JSON."""
    pack = {
        "generated_at": "2026-08-25 12:00",
        "scan_batch": {"label": "2026-08-25 10:00"},
        "framework": {"metadata": {"version": "2026.1"}},
        "recommendation_summary": [
            {
                "#": 1,
                "Type": "New Competency",
                "Confidence": "88%",
                "Sub functional area": "Systems",
                "Competency": "Digital Thread",
                "Supporting sources": 2,
                "Supporting organisations": 2,
                "Source family types": 1,
            }
        ],
        "support_coverage": {
            "source_families": [{"Source family": "Government Agency", "Cited evidence count": 1}],
            "organisations": [{"Organisation": "Org A", "Cited evidence count": 1}],
        },
        "organised_scan_quality": {
            "label": "Structured-heavy",
            "primary_evidence_items": 8,
            "signal_evidence_items": 2,
            "primary_share": 0.8,
        },
        "source_health_counts": {"Healthy": 1, "Low evidence": 1, "No evidence": 0, "Error": 0},
        "source_health": [
            {
                "Status": "Healthy",
                "Evidence items": 8,
                "Organisation": "Org A",
                "Source": "Framework hub",
                "Suggested action": "Keep current crawler",
            },
            {
                "Status": "Low evidence",
                "Evidence items": 2,
                "Organisation": "Org B",
                "Source": "Skills hub",
                "Suggested action": "Review source URL or article limits",
            },
        ],
        "llm_fallback_candidates": [
            {
                "Status": "No evidence",
                "Organisation": "Org C",
                "Source": "Catalogue hub",
                "Source URL": "https://c.example/catalogue",
                "Fallback intent": "Recover STE courses, programmes, certifications, or training resources",
                "Recovery readiness": "Ready for prompt review",
                "Recommended next step": "Review the fallback prompt preview, then decide whether to run a controlled LLM recovery pass.",
            }
        ],
        "llm_fallback_readiness_counts": {
            "Ready for prompt review": 1,
            "Needs access review": 0,
            "Optional signal recovery": 0,
            "Review manually first": 0,
            "Needs source URL": 0,
        },
        "llm_fallback_recoveries": [
            {
                "id": 9,
                "created_at": "2026-08-26 11:30",
                "organisation": "Org C",
                "source_name": "Catalogue hub",
                "source_url": "https://c.example/catalogue",
                "recovered_item_count": 2,
                "result": {"recovered_items": [{"title": "Recovered programme"}]},
            }
        ],
        "recommendations": [
            {
                "recommendation_type": "NEW_COMPETENCY",
                "confidence": 0.88,
                "sub_functional_area": "Systems",
                "competency": "Digital Thread",
                "kind_of_changes_suggested": "Add competency",
                "reasons_for_suggesting_the_changes": "Evidence shows a gap.",
                "support_summary": "2 source(s) · 2 org(s) · 1 source family type(s)",
                "supporting_evidence_ids": [1, 2],
                "supporting_organisations": ["Org A", "Org B"],
                "supporting_urls": ["https://a.example", "https://b.example"],
                "supporting_sources": [
                    {
                        "evidence_id": 1,
                        "title": "Framework page",
                        "organisation": "Org A",
                        "url": "https://a.example",
                        "country": "Singapore",
                        "source_family": "GOVERNMENT_AGENCY",
                        "source_type": "FRAMEWORK",
                        "source_role": "PRIMARY_DISCOVERY",
                    },
                    {
                        "evidence_id": 2,
                        "title": "Survey page",
                        "organisation": "Org B",
                        "url": "https://b.example",
                    },
                ],
            }
        ],
        "source_lookup": {
            10: {
                "organisation": "Org A",
                "country": "Singapore",
                "source_family": "GOVERNMENT_AGENCY",
                "source_type": "FRAMEWORK",
                "source_role": "PRIMARY_DISCOVERY",
            }
        },
        "saved_questions": [
            {"asked_at": "2026-08-25 12:05", "question": "Why?", "answer": "Because evidence supports it."}
        ],
    }

    markdown = _recommendation_pack_markdown(pack)

    assert "# Recommendation Pack" in markdown
    assert "## Organised scan quality" in markdown
    assert "Evidence mix: Structured-heavy · Primary evidence: 8 · Signal evidence: 2 · Primary share: 0.8" in markdown
    assert "| 1 | New Competency | 88% | Systems | Digital Thread | 2 | 2 | 1 |" in markdown
    assert "## Support coverage" in markdown
    assert "| Government Agency | 1 |" in markdown
    assert "## Source health" in markdown
    assert "Healthy: 1 · Low evidence: 1 · No evidence: 0 · Errors: 0" in markdown
    assert "| Low evidence | 2 | Org B | Skills hub | Review source URL or article limits |" in markdown
    assert "## LLM fallback candidates" in markdown
    assert "Ready: 1 · Access review: 0 · Optional signal: 0 · Manual first: 0" in markdown
    assert "| No evidence | Ready for prompt review | Org C | Catalogue hub | https://c.example/catalogue | Recover STE courses, programmes, certifications, or training resources | Review the fallback prompt preview, then decide whether to run a controlled LLM recovery pass. |" in markdown
    assert "## Saved LLM fallback recoveries" in markdown
    assert "| 9 | 2026-08-26 11:30 | Org C | Catalogue hub | 2 | No advice recorded | https://c.example/catalogue |" in markdown
    assert "### 1. New Competency · 88%" in markdown
    assert "- [Evidence 1] Framework page — Org A (government agency, framework, primary discovery, singapore): https://a.example" in markdown
    assert "- [Evidence 2] Survey page — Org B: https://b.example" in markdown
    assert "## Saved Ask AI questions" in markdown


def test_recommendation_pack_markdown_escapes_table_breaking_text() -> None:
    """Markdown export should survive pipes and newlines in officer-facing text."""
    pack = {
        "generated_at": "2026-08-25 12:00",
        "scan_batch": {"label": "2026-08-25 10:00"},
        "framework": {"metadata": {"version": "2026.1"}},
        "recommendation_summary": [
            {
                "#": 1,
                "Type": "New | Competency",
                "Confidence": "88%",
                "Sub functional area": "Systems\nEngineering",
                "Competency": "Digital | Thread",
                "Supporting sources": 2,
                "Supporting organisations": 2,
                "Source family types": 1,
            }
        ],
        "recommendations": [
            {
                "recommendation_type": "NEW_COMPETENCY",
                "confidence": 0.88,
                "sub_functional_area": "Systems\nEngineering",
                "competency": "Digital | Thread",
                "kind_of_changes_suggested": "Add | competency",
                "reasons_for_suggesting_the_changes": "Evidence\nshows | a gap.",
                "support_summary": "2 source(s)",
                "supporting_organisations": ["Org | A"],
                "supporting_urls": ["https://a.example"],
            }
        ],
        "saved_questions": [],
    }

    markdown = _recommendation_pack_markdown(pack)

    assert "New \\| Competency" in markdown
    assert "Systems Engineering" in markdown
    assert "Digital \\| Thread" in markdown
    assert "Evidence shows \\| a gap." in markdown
    assert "- Org \\| A: https://a.example" in markdown


def test_recommendation_summary_csv_exports_table_rows_for_spreadsheets() -> None:
    """Recommendation summary can be downloaded for spreadsheet review."""
    rows = [
        {
            "#": 1,
            "Type": "New Competency",
            "Confidence": "88%",
            "Sub functional area": "Systems",
            "Competency": "Digital Thread",
            "Supporting sources": 2,
            "Supporting organisations": 2,
            "Source family types": 1,
        }
    ]

    csv_text = _recommendation_summary_csv(rows)

    assert csv_text.splitlines()[0] == "#,Type,Confidence,Sub functional area,Competency,Supporting sources,Supporting organisations,Source family types"
    assert "1,New Competency,88%,Systems,Digital Thread,2,2,1" in csv_text


def test_question_history_exports_saved_ask_ai_discussion() -> None:
    """Saved Ask AI questions can be exported without downloading the full recommendation pack."""
    rows = [
        _QuestionRow(
            {
                "id": 1,
                "asked_at": "2026-08-25T14:03:00",
                "question": "Which recommendation is strongest?",
                "answer": "Recommendation 2 has broad support.",
            }
        )
    ]

    csv_text = _question_history_csv(rows)
    markdown = _question_history_markdown(rows, "2026-08-25 14:00")

    assert csv_text.splitlines()[0] == "Asked at,Question,Answer"
    assert "2026-08-25 14:03,Which recommendation is strongest?,Recommendation 2 has broad support." in csv_text
    assert "# Ask AI Question History" in markdown
    assert "## Conversation summary" in markdown
    assert "Themes: Evidence strength" in markdown
    assert "Batch: 2026-08-25 14:00" in markdown
    assert "Question: Which recommendation is strongest?" in markdown
    assert "Answer: Recommendation 2 has broad support." in markdown


def test_question_history_summary_is_compact_and_thematic() -> None:
    """Saved Ask AI discussion should have a compact batch-level summary."""
    rows = [
        _QuestionRow({"id": 1, "asked_at": "2026-08-25T14:03:00", "question": "Which source evidence is strongest?", "answer": "Professional body support is strongest."}),
        _QuestionRow({"id": 2, "asked_at": "2026-08-25T14:08:00", "question": "Any outlier signals?", "answer": "There is one emerging signal."}),
    ]

    summary = _question_history_summary(rows)

    assert summary["question_count"] == 2
    assert summary["first_question_at"] == "2026-08-25 14:03"
    assert summary["latest_question_at"] == "2026-08-25 14:08"
    assert "Evidence strength" in summary["common_review_themes"]
    assert "Outlier or trend signals" in summary["common_review_themes"]
    assert len(summary["recent_questions"]) == 2
