from types import SimpleNamespace
import pytest
from src.services.source_health_service import source_health_rows, ICHEME_DOCUMENT_ROOT, ICHEME_EXPECTED_DOCUMENTS


@pytest.mark.parametrize('complete,error,expected', [(True, False, 'Healthy'), (False, False, 'Low evidence'), (True, True, 'Error')])
def test_reviewed_document_completeness_does_not_hide_errors(complete, error, expected):
    run = SimpleNamespace(error_summary='IChemE: skipped page' if error else '',
        sources_snapshot=[{'id': 1, 'name': 'IChemE', 'url': ICHEME_DOCUMENT_ROOT}])
    urls = sorted(ICHEME_EXPECTED_DOCUMENTS)
    evidence = [SimpleNamespace(source_id=1, url=u) for u in (urls if complete else urls[:2])]
    row = source_health_rows(run, evidence)[0]
    assert row['Status'] == expected
    if expected == 'Healthy':
        assert 'inspect content quality separately' in row['Reason']


def test_other_sources_and_duplicate_urls_cannot_complete_document_set():
    run = SimpleNamespace(error_summary='', sources_snapshot=[{'id': 1, 'name': 'IChemE', 'url': ICHEME_DOCUMENT_ROOT}])
    urls = sorted(ICHEME_EXPECTED_DOCUMENTS)
    evidence = [SimpleNamespace(source_id=1, url=urls[0])]*3
    evidence += [SimpleNamespace(source_id=2, url=u) for u in urls]
    assert source_health_rows(run, evidence)[0]['Status'] == 'Low evidence'
