import inspect

import pytest
from src.core.exceptions import RecommendationError
from src.llm.competency_analyst import OpenAICompetencyAnalyst


def test_ask_ai_rejects_oversized_context_before_api_call(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-not-a-real-key')
    def forbidden_client():
        pytest.fail('Oversized context must not call OpenAI')
    monkeypatch.setattr('src.llm.competency_analyst.OpenAI', forbidden_client)
    analyst = object.__new__(OpenAICompetencyAnalyst)
    with pytest.raises(RecommendationError, match='no request was sent'):
        analyst.answer_question({'framework': 'X' * 300_001}, 'Why?')


def test_parse_response_accepts_valid_recommendation() -> None:
    """Strict parsing keeps recommendation content explainable."""
    result = OpenAICompetencyAnalyst._parse_response('{"recommendations":[{"recommendation_type":"NEW_COMPETENCY","confidence":0.8,"reasoning":"Evidence identifies a gap.","sub_functional_area":"AI","competency":"Data literacy","kind_of_changes_suggested":"Refine the competency wording","reasons_for_suggesting_the_changes":"Definitions indicate a broader scope.","supporting_evidence_ids":[1],"supporting_urls":["https://example.com"],"supporting_organisations":["Example"]}]}')
    assert result[0].recommendation_type == "NEW_COMPETENCY"


def test_parse_response_accepts_outlier_signal_recommendation() -> None:
    """Outlier signals are visible monitoring recommendations, not hidden categories."""
    result = OpenAICompetencyAnalyst._parse_response('{"recommendations":[{"recommendation_type":"OUTLIER_SIGNAL_DETECTED","confidence":0.72,"reasoning":"A reputable institute shows a new STE course combination worth monitoring.","sub_functional_area":"AI Engineering Signals","competency":"AI safety testing with systems engineering","kind_of_changes_suggested":"Monitor outlier signal before framework adoption","reasons_for_suggesting_the_changes":"The evidence is credible but not yet broad enough for immediate framework change.","supporting_evidence_ids":[1,2],"supporting_urls":["https://example.com/a","https://example.com/b"],"supporting_organisations":["Example University","Example Agency"]}]}')

    assert result[0].recommendation_type == "OUTLIER_SIGNAL_DETECTED"
    assert result[0].kind_of_changes_suggested == "Monitor outlier signal before framework adoption"


def test_parse_response_hides_weak_deprecation_candidate() -> None:
    """Deprecation candidates need stronger positive evidence than ordinary recommendations."""
    result = OpenAICompetencyAnalyst._parse_response('{"recommendations":[{"recommendation_type":"DEPRECATION_CANDIDATE","confidence":0.7,"reasoning":"The model thinks this competency may be outdated.","sub_functional_area":"Legacy Systems","competency":"Legacy tool operation","kind_of_changes_suggested":"Review for deletion","reasons_for_suggesting_the_changes":"Only one source suggests a replacement.","supporting_evidence_ids":[1],"supporting_urls":["https://example.com/a"],"supporting_organisations":["Example"]}]}')

    assert result[0].recommendation_type == "INSUFFICIENT_EVIDENCE"
    assert "weak deprecation candidate downgraded" in result[0].reasoning


def test_parse_response_accepts_strong_deprecation_candidate() -> None:
    """Well-supported deprecation candidates can remain visible for human review."""
    result = OpenAICompetencyAnalyst._parse_response('{"recommendations":[{"recommendation_type":"DEPRECATION_CANDIDATE","confidence":0.82,"reasoning":"Four official sources indicate the competency has been superseded.","sub_functional_area":"Legacy Systems","competency":"Legacy tool operation","kind_of_changes_suggested":"Human-review deprecation candidate only","reasons_for_suggesting_the_changes":"Evidence shows the competency has been replaced by newer standards and course guidance.","supporting_evidence_ids":[1,2,3,4],"supporting_urls":["https://example.com/a","https://example.com/b","https://example.com/c","https://example.com/d"],"supporting_organisations":["Example A","Example B","Example C","Example D"]}]}')

    assert result[0].recommendation_type == "DEPRECATION_CANDIDATE"


def test_parse_response_rejects_non_json() -> None:
    """No prose model output is allowed into persistence."""
    with pytest.raises(RecommendationError, match="valid JSON"):
        OpenAICompetencyAnalyst._parse_response("Here are the recommendations")


def test_response_schema_requires_a_closed_recommendation_shape() -> None:
    """Structured Outputs prevents additional model-generated fields."""
    from src.llm.competency_analyst import MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION, MIN_DEPRECATION_SUPPORTING_SOURCES, RESPONSE_SCHEMA
    item_schema = RESPONSE_SCHEMA["properties"]["recommendations"]["items"]
    recommendations_schema = RESPONSE_SCHEMA["properties"]["recommendations"]
    assert RESPONSE_SCHEMA["additionalProperties"] is False
    assert item_schema["additionalProperties"] is False
    assert recommendations_schema["maxItems"] == 20
    assert item_schema["required"] == [
        "recommendation_type",
        "confidence",
        "reasoning",
        "sub_functional_area",
        "competency",
        "kind_of_changes_suggested",
        "reasons_for_suggesting_the_changes",
        "supporting_evidence_ids",
        "supporting_urls",
        "supporting_organisations",
    ]
    assert "ALREADY_COVERED" in item_schema["properties"]["recommendation_type"]["enum"]
    assert "INSUFFICIENT_EVIDENCE" in item_schema["properties"]["recommendation_type"]["enum"]
    assert "OUTLIER_SIGNAL_DETECTED" in item_schema["properties"]["recommendation_type"]["enum"]
    assert item_schema["properties"]["supporting_evidence_ids"]["maxItems"] == MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION
    assert item_schema["properties"]["supporting_urls"]["maxItems"] == MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION
    assert item_schema["properties"]["supporting_organisations"]["maxItems"] == MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION
    assert MIN_DEPRECATION_SUPPORTING_SOURCES == 4


def test_prompt_uses_organised_scan_and_selected_evidence_layers() -> None:
    """The model should receive full-batch structure separately from citation details."""
    prompt = OpenAICompetencyAnalyst._build_prompt(
        {"version": "test", "sub_functional_areas": []},
        {
            "organised_scan": {"total_evidence_items": 100, "organisations": []},
            "selected_evidence": [{"id": 1, "title": "Evidence"}],
        },
    )

    assert "ORGANISED_SCAN" in prompt
    assert "SELECTED_EVIDENCE" in prompt
    assert "full-batch coverage map" in prompt
    assert "ORGANISED_SCAN.quality_summary" in prompt
    assert "cite 4 to 10 supporting_evidence_ids" in prompt
    assert "OUTLIER_SIGNAL_DETECTED" in prompt
    assert "worth monitoring but not yet broad enough for immediate framework change" in prompt
    assert "do not rely on absence of evidence" in prompt
    assert "human-review deprecation candidate" in prompt


def test_question_answer_prompt_uses_source_health_context() -> None:
    """Ask AI should consider source-health diagnostics when discussing scan reliability."""
    source = inspect.getsource(OpenAICompetencyAnalyst.answer_question)

    assert "organised_scan_quality" in source
    assert "source_health" in source
    assert "scan reliability" in source
    assert "LLM fallback" in source
    assert "llm_fallback_candidates" in source
    assert "llm_fallback_readiness_counts" in source
    assert "llm_fallback_request_preview" in source
