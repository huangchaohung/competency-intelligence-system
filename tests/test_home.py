from types import SimpleNamespace

from src.dashboard.home import _attention_rows_csv, _sources_needing_attention, _validation_checkpoint


def test_sources_needing_attention_excludes_healthy_sources() -> None:
    """Home should highlight only sources that need tuning or fallback review."""
    rows = [
        {"Status": "Healthy", "Source": "A"},
        {"Status": "Low evidence", "Source": "B"},
        {"Status": "No evidence", "Source": "C"},
        {"Status": "Error", "Source": "D"},
    ]

    assert _sources_needing_attention(rows) == [
        {"Status": "Low evidence", "Source": "B"},
        {"Status": "No evidence", "Source": "C"},
        {"Status": "Error", "Source": "D"},
    ]


def test_attention_rows_csv_exports_home_action_list() -> None:
    """Home attention list can be downloaded for quick source follow-up."""
    rows = [
        {
            "Status": "Error",
            "Evidence items": 0,
            "Organisation": "Org A",
            "Source": "Broken Source",
            "Suggested action": "Consider LLM fallback",
            "Extra": "Ignored",
        }
    ]

    csv_text = _attention_rows_csv(rows)

    assert csv_text.splitlines()[0] == "Status,Evidence items,Organisation,Source,Suggested action"
    assert "Error,0,Org A,Broken Source,Consider LLM fallback" in csv_text


def test_validation_checkpoint_guides_no_scan_state() -> None:
    """Home should tell officers when the next useful check is basic UI review."""
    checkpoint = _validation_checkpoint()

    assert checkpoint["Checkpoint"] == "Open Streamlit for UIUX review"
    assert "Source Configuration" in checkpoint["Suggested action"]


def test_validation_checkpoint_guides_source_quality_review() -> None:
    """Home should point to source tuning when the latest scan has empty/error sources."""
    latest_run = SimpleNamespace(status=SimpleNamespace(value="COMPLETED_WITH_ERRORS"))
    health_rows = [{"Status": "No evidence"}, {"Status": "Healthy"}]

    checkpoint = _validation_checkpoint(latest_run, ["evidence"], health_rows)

    assert checkpoint["Checkpoint"] == "Review source quality and fallback candidates"
    assert "controlled fallback recovery" in checkpoint["Suggested action"]


def test_validation_checkpoint_guides_recommendation_review_after_stable_scan() -> None:
    """Home should suggest recommendation/UIUX review once evidence and source health are stable."""
    latest_run = SimpleNamespace(status=SimpleNamespace(value="COMPLETED"))

    checkpoint = _validation_checkpoint(latest_run, ["evidence"], [{"Status": "Healthy"}])

    assert checkpoint["Checkpoint"] == "Open Streamlit for recommendation and UIUX review"
    assert "Recommendations and History" in checkpoint["Suggested action"]
