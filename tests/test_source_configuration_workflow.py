from src.core.database import connect, initialise
from src.models.domain import Source
from src.repositories.source_repository import SourceRepository
from src.services.configuration_service import ConfigurationService
from src.services.source_service import SourceService
from src.workflow.source_configuration_workflow import SourceConfigurationWorkflow


def test_upsert_persists_source_to_configuration_and_database(tmp_path) -> None:
    """Officer changes remain durable and are immediately available for scans."""
    path = tmp_path / "sources.yaml"
    path.write_text("sources: []\n", encoding="utf-8")
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    configuration = ConfigurationService(path)
    workflow = SourceConfigurationWorkflow(configuration, SourceService(SourceRepository(connection)))
    saved = workflow.upsert(Source(None, "Focused reports", "https://example.com/reports", "Example Organisation", "Unknown", True, "Government agencies and public institutions"))
    assert saved.id is not None
    configured = configuration.load_sources()[0]
    assert configured.url == "https://example.com/reports"
    assert configured.enabled is True


def test_upsert_replaces_existing_source_when_url_changes(tmp_path) -> None:
    """Changing a scan target updates the source instead of creating a duplicate."""
    path = tmp_path / "sources.yaml"
    path.write_text("sources:\n  - name: Test\n    url: https://example.com/home\n    organisation: Example\n", encoding="utf-8")
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    configuration = ConfigurationService(path)
    repository = SourceRepository(connection)
    source_service = SourceService(repository)
    existing = source_service.synchronise(configuration.load_sources())[0]
    workflow = SourceConfigurationWorkflow(configuration, source_service)
    updated = workflow.upsert(Source(None, "Focused reports", "https://example.com/reports", "Example", "Unknown", True), previous_url=existing.url, previous_id=existing.id)
    assert updated.id == existing.id
    assert [item.url for item in repository.list_all()] == ["https://example.com/reports"]


def test_remove_uses_url_when_configuration_sources_have_no_database_ids(tmp_path) -> None:
    """Removing from the UI should update YAML even though loaded YAML sources have no IDs."""
    path = tmp_path / "sources.yaml"
    path.write_text(
        "sources:\n"
        "  - name: Keep\n"
        "    url: https://example.com/keep\n"
        "    organisation: Example\n"
        "  - name: Remove\n"
        "    url: https://example.com/remove\n"
        "    organisation: Example\n",
        encoding="utf-8",
    )
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    configuration = ConfigurationService(path)
    repository = SourceRepository(connection)
    source_service = SourceService(repository)
    persisted = source_service.synchronise(configuration.load_sources())
    removed = next(source for source in persisted if source.url == "https://example.com/remove")
    workflow = SourceConfigurationWorkflow(configuration, source_service)

    workflow.remove(removed.id or 0, removed.url)

    assert [source.url for source in configuration.load_sources()] == ["https://example.com/keep"]
    assert [source.url for source in repository.list_all()] == ["https://example.com/keep"]


def test_stage_test_set_enables_only_requested_sources(tmp_path) -> None:
    """Controlled tuning stages leave the catalogue intact but isolate the scan set."""
    path = tmp_path / "sources.yaml"
    path.write_text(
        "sources:\n"
        "  - name: NASA Handbook\n    url: https://nasa.example/handbook\n    organisation: NASA\n    enabled: false\n"
        "  - name: Other\n    url: https://example.com/other\n    organisation: Other Org\n    enabled: true\n",
        encoding="utf-8",
    )
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    configuration = ConfigurationService(path)
    repository = SourceRepository(connection)
    source_service = SourceService(repository)
    source_service.synchronise(configuration.load_sources())
    workflow = SourceConfigurationWorkflow(configuration, source_service)

    workflow.stage_test_set(["NASA Handbook"])

    assert [source.name for source in repository.list_enabled()] == ["NASA Handbook"]
    assert len(configuration.load_sources()) == 2
    assert configuration.load_sources()[1].enabled is False


def test_stage_test_set_rejects_unknown_identifier(tmp_path) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text("sources:\n  - name: One\n    url: https://example.com/one\n    organisation: Org\n", encoding="utf-8")
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    configuration = ConfigurationService(path)
    workflow = SourceConfigurationWorkflow(configuration, SourceService(SourceRepository(connection)))

    import pytest
    with pytest.raises(ValueError, match="Unknown source"):
        workflow.stage_test_set(["Missing"])
