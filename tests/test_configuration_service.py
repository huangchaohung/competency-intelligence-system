from pathlib import Path
import pytest
from src.core.exceptions import ConfigurationError
from src.models.domain import SourceRole, SourceType
from src.services.configuration_service import ConfigurationService


def test_load_sources_rejects_non_https_url(tmp_path: Path) -> None:
    """Only HTTPS public sources are permitted."""
    path = tmp_path / "sources.yaml"
    path.write_text("sources:\n  - name: Test\n    url: http://example.com\n    organisation: Test", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="HTTPS"):
        ConfigurationService(path).load_sources()


def test_load_sources_preserves_catalogue_category(tmp_path: Path) -> None:
    """Source category remains configuration data."""
    path = tmp_path / "sources.yaml"
    path.write_text("sources:\n  - name: Test\n    url: https://example.com\n    organisation: Test\n    category: Government agencies and public institutions\n", encoding="utf-8")
    source = ConfigurationService(path).load_sources()[0]
    assert source.category == "Government agencies and public institutions"


def test_load_sources_infers_strategy_from_evidence_label(tmp_path: Path) -> None:
    """Unspecified source strategy is inferred from the source evidence intent."""
    path = tmp_path / "sources.yaml"
    path.write_text(
        "sources:\n"
        "  - name: IEEE AI\n"
        "    url: https://spectrum.ieee.org/topic/artificial-intelligence/\n"
        "    organisation: IEEE\n"
        "    evidence_label: news / commentary\n",
        encoding="utf-8",
    )
    source = ConfigurationService(path).load_sources()[0]
    assert source.source_type == SourceType.TREND
    assert source.source_role == SourceRole.TREND_VALIDATION


def test_load_sources_from_text_validates_backup_without_saving(tmp_path: Path) -> None:
    """Uploaded source backups can be parsed and validated before any restore action."""
    path = tmp_path / "sources.yaml"
    path.write_text("sources: []\n", encoding="utf-8")
    source = ConfigurationService(path).load_sources_from_text(
        "sources:\n"
        "  - name: Test Backup\n"
        "    url: https://example.com/reports\n"
        "    organisation: Example\n"
        "    max_listing_pages: 25\n"
    )[0]

    assert source.name == "Test Backup"
    assert source.max_listing_pages == 25
    assert ConfigurationService(path).load_sources() == []


def test_load_sources_from_text_rejects_invalid_backup(tmp_path: Path) -> None:
    """Backup preview should use the same safety validation as saved catalogues."""
    path = tmp_path / "sources.yaml"
    path.write_text("sources: []\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="HTTPS"):
        ConfigurationService(path).load_sources_from_text("sources:\n  - name: Bad\n    url: http://example.com\n    organisation: Example\n")
