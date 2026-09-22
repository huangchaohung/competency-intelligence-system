"""Local system diagnostics for IT handover and troubleshooting."""
from __future__ import annotations

import importlib.util
import os
import sqlite3
from pathlib import Path
from typing import Any


REQUIRED_IMPORTS = ("streamlit", "requests", "bs4", "lxml", "openai", "openpyxl", "pandas", "yaml", "pypdf")
EXPECTED_TABLES = {
    "schema_migrations",
    "sources",
    "scan_runs",
    "framework_versions",
    "sub_functional_areas",
    "competencies",
    "evidence",
    "recommendation_batches",
    "recommendations",
    "batch_questions",
    "fallback_recoveries",
    "source_url_recommendations",
}


def build_system_diagnostics(project_root: Path) -> dict[str, Any]:
    """Return JSON-safe local diagnostics without exposing secrets."""
    project_root = project_root.resolve()
    database_path = project_root / "data" / "competency_intelligence.db"
    log_path = project_root / "logs" / "operational_audit.jsonl"
    diagnostics = {
        "project_root": str(project_root),
        "python_imports": _import_status(),
        "configuration": {
            "sources_yaml_exists": (project_root / "config" / "sources.yaml").exists(),
            "framework_template_exists": (project_root / "data" / "framework_template.csv").exists(),
            "openai_api_key_configured": bool(os.getenv("OPENAI_API_KEY")),
            "openai_model": os.getenv("OPENAI_MODEL", "gpt-5.6-terra"),
        },
        "database": _database_status(database_path),
        "operational_logging": {
            "log_directory_exists": (project_root / "logs").exists(),
            "active_log_exists": log_path.exists(),
            "active_log_path": str(log_path),
            "active_log_size_bytes": log_path.stat().st_size if log_path.exists() else 0,
            "rotated_log_count": len(list((project_root / "logs").glob("operational_audit.jsonl.*"))) if (project_root / "logs").exists() else 0,
        },
    }
    diagnostics["overall_status"] = _overall_status(diagnostics)
    return diagnostics


def _import_status() -> dict[str, bool]:
    """Return whether required runtime packages can be imported."""
    return {name: importlib.util.find_spec(name) is not None for name in REQUIRED_IMPORTS}


def _database_status(database_path: Path) -> dict[str, Any]:
    """Return non-mutating SQLite diagnostics."""
    if not database_path.exists():
        return {
            "exists": False,
            "path": str(database_path),
            "tables": [],
            "missing_expected_tables": sorted(EXPECTED_TABLES),
            "latest_migration": None,
        }
    try:
        connection = sqlite3.connect(database_path)
        tables = sorted(row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'"))
        latest_migration_row = connection.execute("SELECT MAX(version) FROM schema_migrations").fetchone() if "schema_migrations" in tables else None
        connection.close()
    except sqlite3.Error as error:
        return {
            "exists": True,
            "path": str(database_path),
            "error": str(error),
            "tables": [],
            "missing_expected_tables": sorted(EXPECTED_TABLES),
            "latest_migration": None,
        }
    return {
        "exists": True,
        "path": str(database_path),
        "tables": tables,
        "missing_expected_tables": sorted(EXPECTED_TABLES - set(tables)),
        "latest_migration": latest_migration_row[0] if latest_migration_row else None,
    }


def _overall_status(diagnostics: dict[str, Any]) -> str:
    """Return a compact status label for IT triage."""
    if not all(diagnostics["python_imports"].values()):
        return "Needs dependency review"
    if not diagnostics["configuration"]["sources_yaml_exists"]:
        return "Needs source configuration"
    if not diagnostics["database"]["exists"] or diagnostics["database"].get("missing_expected_tables"):
        return "Needs database initialisation"
    if not diagnostics["configuration"]["openai_api_key_configured"]:
        return "Ready for scan-only use"
    return "Ready"
