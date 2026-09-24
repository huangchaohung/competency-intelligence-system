"""Tests for source catalogue export helpers."""
from __future__ import annotations

import yaml

from src.models.domain import Source, SourceFamily, SourceRole, SourceType
from src.services.source_catalogue_export import source_rows, sources_csv, sources_yaml_backup


def _source() -> Source:
    return Source(
        None,
        "IEEE AI",
        "https://spectrum.ieee.org/topic/artificial-intelligence/",
        "IEEE",
        "Global",
        True,
        "Professional body",
        25,
        r"/topic/",
        True,
        5,
        False,
        "news / commentary",
        SourceType.TREND,
        SourceRole.TREND_VALIDATION,
        True,
        SourceFamily.PROFESSIONAL_BODY,
    )


def test_officer_source_rows_hide_backend_pattern() -> None:
    """Officer exports should not expose crawler regex details."""
    rows = source_rows([_source()])

    assert rows[0]["Name"] == "IEEE AI"
    assert rows[0]["LLM fallback allowed"] == "Yes"
    assert "Article URL pattern" not in rows[0]


def test_it_source_csv_includes_backend_fields() -> None:
    """IT exports should include backend tuning fields."""
    csv_text = sources_csv([_source()], include_backend_fields=True)

    assert "Article URL pattern" in csv_text.splitlines()[0]
    assert "https://spectrum.ieee.org/topic/artificial-intelligence/" in csv_text


def test_source_yaml_backup_matches_configuration_shape() -> None:
    """YAML backup should be loadable as a source configuration document."""
    backup = sources_yaml_backup([_source()])
    document = yaml.safe_load(backup)

    assert list(document) == ["sources"]
    assert document["sources"][0]["name"] == "IEEE AI"
    assert document["sources"][0]["source_family"] == "PROFESSIONAL_BODY"
    assert document["sources"][0]["enabled"] is True
