from types import SimpleNamespace
from src.services.evidence_duplicates import public_description_key


def evidence(slug='example', text='Identical topic description', org='IEEE PES'):
    return SimpleNamespace(url='https://resourcecenter.ieee-pes.org/education/webinars/'+slug,
                           organisation=org,
                           article_text='Public resource description only; full resource not retrieved.\n\n'+text)


def test_same_webinar_slide_description_has_same_identity():
    assert public_description_key(evidence()) == public_description_key(evidence('example_sld'))


def test_different_webinars_and_content_remain_distinct():
    assert public_description_key(evidence()) != public_description_key(evidence('another'))
    assert public_description_key(evidence()) != public_description_key(evidence('example_sld','Additional learning outcomes'))
    assert public_description_key(evidence()) != public_description_key(evidence(org='Other organisation'))


def test_not_a_global_text_deduplicator():
    item = evidence()
    item.url = 'https://university.example/courses/course-1'
    assert public_description_key(item) is None
    item = evidence()
    item.article_text = 'Actual full resource, not a landing description'
    assert public_description_key(item) is None


def test_workflow_deduplication_is_only_within_current_scan():
    from unittest.mock import Mock
    from datetime import datetime
    from src.models.domain import Source, ScanStatus
    from src.workflow.scan_workflow import ScanWorkflow
    base = evidence().url
    source = Source(1, 'IEEE', base, 'IEEE PES')
    sources, scans, scanner, extractor = Mock(), Mock(), Mock(), Mock()
    sources.list_enabled.return_value = [source]
    scans.create_run.return_value = SimpleNamespace(id=1)
    scans.complete_run.return_value = SimpleNamespace(id=1, status=ScanStatus.COMPLETED,
        started_at=datetime.now(), completed_at=datetime.now(), error_summary=None)
    scans.prune_evidence_to_recent_runs.return_value = 0
    scanner.fetch_url.side_effect = lambda url, name: SimpleNamespace(url=url)
    extractor.extract.side_effect = lambda page, *args: evidence(page.url.rsplit('/', 1)[-1])
    workflow = ScanWorkflow(sources, scans, scanner, extractor)
    workflow._router = SimpleNamespace(discover=lambda s: [base, base+'_sld'])
    workflow.run()
    assert scans.add_evidence.call_count == 1
    workflow.run()
    assert scans.add_evidence.call_count == 2
