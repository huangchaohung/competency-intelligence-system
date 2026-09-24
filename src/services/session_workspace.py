"""Private in-memory workspaces. Never persist user catalogues or scan text."""
import csv
import io
import json
import sqlite3
from copy import deepcopy
from pathlib import Path
from threading import Lock

from src.core.database import initialise
from src.core.exceptions import ConfigurationError
from src.extractor.article_extractor import ArticleExtractor
from src.repositories.scan_repository import ScanRepository
from src.repositories.source_repository import SourceRepository
from src.scanner.web_page_scanner import WebPageScanner
from src.services.configuration_service import ConfigurationService
from src.services.source_service import SourceService
from src.workflow.scan_workflow import ScanWorkflow
from src.workflow.source_configuration_workflow import SourceConfigurationWorkflow


class MemoryConfiguration(ConfigurationService):
    def __init__(self, sources):
        self._sources = deepcopy(sources)

    def load_sources(self):
        return deepcopy(self._sources)

    def save_sources(self, sources):
        self.validate_sources(sources)
        self._sources = deepcopy(sources)


def build_session_services(root: Path):
    master = ConfigurationService(root / 'config' / 'sources.yaml').load_sources()
    connection = sqlite3.connect(':memory:', check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys=ON')
    connection.execute('PRAGMA temp_store=MEMORY')
    initialise(connection, allow_legacy_reset=False)
    sources = SourceRepository(connection)
    scans = ScanRepository(connection)
    configuration = MemoryConfiguration(master)
    service = SourceService(sources)
    service.synchronise(master)
    return {
        'connection': connection, 'lock': Lock(), 'session_only': True,
        'source_repository': sources, 'scan_repository': scans,
        'configuration_service': configuration,
        'source_configuration_workflow': SourceConfigurationWorkflow(configuration, service),
        'scan_workflow': ScanWorkflow(sources, scans, WebPageScanner(), ArticleExtractor()),
    }


def clear_current_scan(services):
    """Discard previous round before scanning, including after a failed attempt."""
    with services['connection'] as connection:
        connection.execute('DELETE FROM evidence')
        connection.execute('DELETE FROM scan_summaries')
        connection.execute('DELETE FROM scan_runs')


FIELDS = {
    'Name': 'name', 'Organisation': 'organisation', 'Discovery URL': 'url',
    'Source family': 'source_family', 'Source type': 'source_type',
    'Source role': 'source_role', 'Enabled': 'enabled', 'Browser': 'use_browser_rendering',
    'Browser rendering': 'use_browser_rendering', 'Max articles': 'max_articles_per_scan',
    'Listing pages': 'max_listing_pages',
}


def parse_source_csv(data: bytes, configuration):
    """Accept the downloadable template; reject malformed input before mutation."""
    if len(data) > 1_000_000:
        raise ConfigurationError('Source CSV must be no larger than 1 MB.')
    try:
        reader = csv.DictReader(io.StringIO(data.decode('utf-8-sig')))
        if not {'Name', 'Organisation', 'Discovery URL'} <= set(reader.fieldnames or []):
            raise ConfigurationError('CSV requires Name, Organisation and Discovery URL columns. Use the template.')
        rows = []
        for row in reader:
            if None in row:
                raise ConfigurationError('CSV row has more values than columns.')
            item = {target: row[key].strip() for key, target in FIELDS.items() if (row.get(key) or '').strip()}
            for key in ('enabled', 'use_browser_rendering'):
                if key in item:
                    value = item[key].casefold()
                    if value not in {'true', 'false', 'yes', 'no', '1', '0'}:
                        raise ConfigurationError(f'{key} must be Yes/No or True/False.')
                    item[key] = value in {'true', 'yes', '1'}
            rows.append(item)
            if len(rows) > 500:
                raise ConfigurationError('Upload at most 500 sources at a time.')
        if not rows:
            raise ConfigurationError('The source CSV is empty.')
        return configuration.load_sources_from_text(json.dumps({'sources': rows}))
    except (UnicodeError, ValueError, TypeError, csv.Error) as error:
        raise ConfigurationError(f'Invalid source CSV: {error}') from error


def session_sources_csv(sources):
    stream = io.StringIO()
    columns = list(FIELDS)
    columns.remove('Browser rendering')
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    for source in sources:
        writer.writerow({key: getattr(getattr(source, FIELDS[key]), 'value', getattr(source, FIELDS[key])) for key in columns})
    return stream.getvalue()
