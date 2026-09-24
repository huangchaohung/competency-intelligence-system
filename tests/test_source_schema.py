from src.core.database import connect, initialise
from src.models.domain import Source, SourceType
from src.repositories.source_repository import SourceRepository
from src.services.configuration_service import ConfigurationService


def test_removed_columns_and_research_roundtrip(tmp_path):
    connection = connect(tmp_path / 'db.sqlite')
    initialise(connection)
    columns = {r[1] for r in connection.execute('PRAGMA table_info(sources)')}
    assert not {'country', 'category', 'evidence_label'}.intersection(columns)
    repo = SourceRepository(connection)
    saved = repo.upsert(Source(None, 'Research', 'https://example.org/research', 'Org', evidence_label='research / report'))
    assert saved.source_type == SourceType.RESEARCH
    config = ConfigurationService(tmp_path / 'sources.yaml')
    config.save_sources([saved])
    assert config.load_sources()[0].source_type == SourceType.RESEARCH
    text = (tmp_path / 'sources.yaml').read_text()
    assert all(field + ':' not in text for field in ('country', 'category', 'evidence_label'))
    initialise(connection)
    assert repo.list_all()[0].id == saved.id
    connection.close()


def test_upgrade_preserves_identity_and_old_snapshot(tmp_path):
    connection = connect(tmp_path / 'db.sqlite')
    initialise(connection)
    saved = SourceRepository(connection).upsert(Source(None, 'Old', 'https://example.org', 'Org'))
    for field in ('country', 'category', 'evidence_label'):
        connection.execute(f'ALTER TABLE sources ADD COLUMN {field} TEXT')
    connection.execute("UPDATE sources SET evidence_label='research / report'")
    connection.execute("INSERT INTO scan_runs(started_at,status,sources_snapshot) VALUES('2026-09-24','COMPLETED','[{\"country\":\"Singapore\"}]')")
    connection.execute('DELETE FROM schema_migrations WHERE version=20')
    connection.commit()
    initialise(connection)
    result = SourceRepository(connection).list_all()[0]
    assert result.id == saved.id and result.source_type == SourceType.RESEARCH
    assert 'Singapore' in connection.execute('SELECT sources_snapshot FROM scan_runs').fetchone()[0]
    connection.close()
