"""SQLite persistence for the active source configuration."""
from src.models.domain import Source, SourceFamily, SourceRole, SourceType
from src.services.source_schema import migrated_type


class SourceRepository:
    FIELDS = ('name', 'url', 'organisation', 'source_family', 'source_type', 'source_role',
              'llm_allowed', 'enabled', 'max_articles_per_scan', 'article_url_pattern',
              'is_active', 'max_listing_pages', 'use_browser_rendering')

    def __init__(self, connection):
        self._connection = connection

    @classmethod
    def _values(cls, source):
        values = []
        for field in cls.FIELDS:
            value = getattr(source, field)
            if field == 'source_type':
                value = migrated_type(value, source.evidence_label)
            values.append(value.value if hasattr(value, 'value') else value)
        return tuple(values)

    def upsert(self, source):
        columns = ','.join(self.FIELDS)
        marks = ','.join('?' for _ in self.FIELDS)
        updates = ','.join(f'{f}=excluded.{f}' for f in self.FIELDS if f != 'url')
        self._connection.execute(f'INSERT INTO sources({columns}) VALUES({marks}) ON CONFLICT(url) DO UPDATE SET {updates}', self._values(source))
        self._connection.commit()
        return self._to_source(self._connection.execute('SELECT * FROM sources WHERE url=?', (source.url,)).fetchone())

    def update(self, source):
        if source.id is None:
            raise ValueError('A source ID is required for update')
        assignments = ','.join(f'{f}=?' for f in self.FIELDS)
        self._connection.execute(f'UPDATE sources SET {assignments} WHERE id=?', self._values(source) + (source.id,))
        self._connection.commit()
        row = self._connection.execute('SELECT * FROM sources WHERE id=?', (source.id,)).fetchone()
        if row is None:
            raise ValueError(f'Source does not exist: {source.id}')
        return self._to_source(row)

    def list_enabled(self):
        return [self._to_source(r) for r in self._connection.execute('SELECT * FROM sources WHERE enabled=1 AND is_active=1 ORDER BY name')]

    def list_all(self):
        return [self._to_source(r) for r in self._connection.execute('SELECT * FROM sources WHERE is_active=1 ORDER BY name')]

    def retire_missing(self, active_urls):
        if active_urls:
            marks = ','.join('?' for _ in active_urls)
            self._connection.execute(f'UPDATE sources SET is_active=0, enabled=0 WHERE url NOT IN ({marks})', tuple(active_urls))
        else:
            self._connection.execute('UPDATE sources SET is_active=0, enabled=0')
        self._connection.commit()

    @staticmethod
    def _to_source(row):
        fields = {field: row[field] for field in SourceRepository.FIELDS}
        for key in ('enabled', 'is_active', 'use_browser_rendering', 'llm_allowed'):
            fields[key] = bool(fields[key])
        for key, enum in [('source_type', SourceType), ('source_family', SourceFamily), ('source_role', SourceRole)]:
            fields[key] = enum(fields[key])
        return Source(id=row['id'], **fields)
