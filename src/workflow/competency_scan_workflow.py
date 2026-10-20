"""Session-only card collection using the bounded CSV-pilot collector."""
from dataclasses import asdict
from datetime import datetime
from urllib.parse import urlsplit
from uuid import uuid4

from src.models.domain import Evidence, ScanStatus
from src.scanner.competency_pilot import PilotCollector


class CompetencyScanWorkflow:
    def __init__(self, sources, scans, plan, collector_factory=PilotCollector):
        self.sources, self.scans, self.plan = sources, scans, plan
        self.collector_factory = collector_factory
        self.result = None

    def run(self, progress_callback=None):
        self.result = None
        sources = self.sources.list_enabled()
        export_id = uuid4().hex
        run = self.scans.create_run(datetime.now().astimezone(), [asdict(s) for s in sources])
        collector = self.collector_factory()
        rows, errors = [], []
        for i, source in enumerate(sources, 1):
            settings = next((p for p in self.plan if p['organisation'] == source.organisation and p['url'] == source.url), {})
            row = dict(Scan_ID=f'S{source.id}', Parent_organisation=source.organisation,
                       Organisation_as_listed=source.organisation, Source_family=source.source_family.value,
                       Mode=settings.get('mode', 'SCAN'), Source_type='UNKNOWN_UNTIL_FETCHED', URL=source.url,
                       Allowed_domains=settings.get('allowed_domains') or urlsplit(source.url).hostname.removeprefix('www.'),
                       Export_id=export_id,
                       Max_cards=min(4, source.max_articles_per_scan), Max_chars_per_card=3000, Max_chars_per_organisation=15000,
                       Browser_rendering='Required' if source.use_browser_rendering and settings.get('browser_required') else ('Yes' if source.use_browser_rendering else 'No'),
                       Page_types_to_find=settings.get('page_types_to_find', 'competency curriculum courses standards'), Notes='', Host_retry=True)
            rows.append(row)
            if progress_callback:
                progress_callback(i, len(sources), source.name, source.source_family.value, source.source_type.value, 'start')
            start = len(collector.cards)
            try:
                collector.run([row])
            except Exception as error:
                collector.log(row, source.url, reason=f'ROW_FAILED: {type(error).__name__}: {str(error)[:160]}')
            new = collector.cards[start:]
            for card in new:
                self.scans.add_evidence(Evidence(None, run.id, source.id,
                    'EXPLICIT_COMPETENCY' if card['source_type'] == 'FRAMEWORK' else 'COURSE',
                    card['title'], None, card['parent_organisation'], card['url'], card['article_text'],
                    datetime.now().astimezone(), 'EXPLICIT'))
            if not new:
                errors.append(source.name + ': No new qualifying cards; see URL log for policy, content or budget reasons.')
            if progress_callback:
                progress_callback(i, len(sources), source.name, source.source_family.value, source.source_type.value, 'done' if new else 'error')
        collector.summarise(rows)
        for status in collector.statuses:
            status['crawler_outcome'] = status['Status']
            if not status['cards_produced']:
                status['Status'] = 'CRAWLER_UNAVAILABLE'
            status['limitations'] = 'Partial deterministic excerpts; no human review. Do not infer omitted text, complete inventories or PDF table relationships. Missing cards do not prove obsolescence.'
        completed = self.scans.complete_run(run, ScanStatus.COMPLETED_WITH_ERRORS if errors else ScanStatus.COMPLETED, '; '.join(errors) or None)
        self.result = dict(run_id=run.id, export_id=export_id, cards=collector.cards, logs=collector.logs, statuses=collector.statuses)
        return completed
