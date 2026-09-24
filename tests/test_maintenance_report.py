"""Tests for the Markdown maintenance report."""
from __future__ import annotations

from src.core.database import connect, initialise
from src.services import maintenance_report
from src.services.operational_logger import OperationalLogger
from src.services.maintenance_report import build_maintenance_report
from src.services.system_diagnostics import REQUIRED_IMPORTS


def _all_required_imports_available() -> dict[str, bool]:
    return {name: True for name in REQUIRED_IMPORTS}


def test_maintenance_report_combines_readiness_and_log_summary(tmp_path, monkeypatch) -> None:
    """The report should be readable enough to paste into an IT handover note."""
    monkeypatch.setattr(maintenance_report, "build_system_diagnostics", lambda project_root: {
        "overall_status": "Ready",
        "project_root": str(project_root),
        "python_imports": _all_required_imports_available(),
        "configuration": {
            "sources_yaml_exists": True,
            "framework_template_exists": True,
            "openai_api_key_configured": True,
            "openai_model": "test-model",
        },
        "database": {
            "exists": True,
            "latest_migration": 18,
            "missing_expected_tables": [],
        },
    })
    (tmp_path / "logs").mkdir()
    logger = OperationalLogger(tmp_path / "logs")
    logger.event("scan_started", {"scan_run_id": 1})
    logger.event("source_urls_discovered", {"source_name": "IEEE", "url_count": 30})
    logger.event("source_scan_completed", {"source_name": "IEEE", "stored_evidence_count": 25})
    logger.event("source_scan_failed", {"source_name": "Blocked Source", "error": "403 Client Error"})
    logger.event("llm_recommendation_response", {"usage": {"input_tokens": 100, "output_tokens": 25}})

    report = build_maintenance_report(tmp_path)

    assert "# STE Competency Intelligence Maintenance Report" in report
    assert "- Status: Ready" in report
    assert "- OpenAI API key configured: Yes" in report
    assert "- `streamlit`: Yes" in report
    assert "- Sources completed: 1" in report
    assert "- Sources failed: 1" in report
    assert "- Evidence stored: 25" in report
    assert "## Source outcomes from logs" in report
    assert "| Blocked Source | 0 | 1 | 0 | 0 | 403 Client Error |" in report
    assert "| IEEE | 1 | 0 | 30 | 25 | - |" in report
    assert "- Total tokens: 125" in report


def test_maintenance_report_can_use_real_diagnostics_without_secrets(tmp_path, monkeypatch) -> None:
    """Real diagnostics should remain secret-safe in the generated Markdown."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-sensitive-test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setattr("src.services.system_diagnostics._import_status", _all_required_imports_available)
    (tmp_path / "config").mkdir()
    (tmp_path / "data").mkdir()
    (tmp_path / "config" / "sources.yaml").write_text("sources: []", encoding="utf-8")
    (tmp_path / "data" / "framework_template.csv").write_text("Cap Area,Sub Functional Area,Competency,Definition\n", encoding="utf-8")
    connection = connect(tmp_path / "data" / "competency_intelligence.db")
    initialise(connection)
    connection.close()

    report = build_maintenance_report(tmp_path)

    assert "- Status: Ready" in report
    assert "sk-sensitive-test-key" not in report
