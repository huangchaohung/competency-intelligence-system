"""Tests for local IT handover diagnostics."""
from __future__ import annotations

import json

from src.core.database import connect, initialise
from src.services import system_diagnostics
from src.services.system_diagnostics import build_system_diagnostics


def _all_required_imports_available() -> dict[str, bool]:
    return {name: True for name in system_diagnostics.REQUIRED_IMPORTS}


def test_system_diagnostics_reports_ready_without_exposing_api_key(tmp_path, monkeypatch) -> None:
    """Diagnostics should be useful for IT while staying secret-safe."""
    monkeypatch.setattr(system_diagnostics, "_import_status", _all_required_imports_available)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-sensitive-test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    (tmp_path / "config").mkdir()
    (tmp_path / "data").mkdir()
    (tmp_path / "logs").mkdir()
    (tmp_path / "config" / "sources.yaml").write_text("sources: []", encoding="utf-8")
    (tmp_path / "data" / "framework_template.csv").write_text("Cap Area,Sub Functional Area,Competency,Definition\n", encoding="utf-8")
    (tmp_path / "logs" / "operational_audit.jsonl").write_text('{"event":"test"}\n', encoding="utf-8")
    connection = connect(tmp_path / "data" / "competency_intelligence.db")
    initialise(connection)
    connection.close()

    diagnostics = build_system_diagnostics(tmp_path)

    assert diagnostics["overall_status"] == "Ready"
    assert diagnostics["configuration"]["openai_api_key_configured"] is True
    assert diagnostics["configuration"]["openai_model"] == "test-model"
    assert diagnostics["database"]["missing_expected_tables"] == []
    assert diagnostics["operational_logging"]["active_log_exists"] is True
    assert "sk-sensitive-test-key" not in json.dumps(diagnostics)


def test_system_diagnostics_reports_scan_only_when_openai_key_missing(tmp_path, monkeypatch) -> None:
    """A missing OpenAI key should not block deterministic scan-only use."""
    monkeypatch.setattr(system_diagnostics, "_import_status", _all_required_imports_available)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    (tmp_path / "config").mkdir()
    (tmp_path / "data").mkdir()
    (tmp_path / "config" / "sources.yaml").write_text("sources: []", encoding="utf-8")
    (tmp_path / "data" / "framework_template.csv").write_text("Cap Area,Sub Functional Area,Competency,Definition\n", encoding="utf-8")
    connection = connect(tmp_path / "data" / "competency_intelligence.db")
    initialise(connection)
    connection.close()

    diagnostics = build_system_diagnostics(tmp_path)

    assert diagnostics["overall_status"] == "Ready for scan-only use"
    assert diagnostics["configuration"]["openai_api_key_configured"] is False


def test_system_diagnostics_reports_database_initialisation_needed(tmp_path, monkeypatch) -> None:
    """IT should see a clear status when the SQLite database has not been created."""
    monkeypatch.setattr(system_diagnostics, "_import_status", _all_required_imports_available)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-sensitive-test-key")
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "sources.yaml").write_text("sources: []", encoding="utf-8")

    diagnostics = build_system_diagnostics(tmp_path)

    assert diagnostics["overall_status"] == "Needs database initialisation"
    assert diagnostics["database"]["exists"] is False
    assert "evidence" in diagnostics["database"]["missing_expected_tables"]
