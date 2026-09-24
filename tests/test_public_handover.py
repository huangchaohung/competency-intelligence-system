import hashlib
import json
from dataclasses import replace
from datetime import datetime, timezone
from io import BytesIO
from zipfile import ZipFile
import pytest
from src.models.domain import ScanRun, ScanStatus, Evidence
from src.services.public_handover import build_handover, zip_handover


def fixture():
    now = datetime.now(timezone.utc)
    run = ScanRun(10, now, now, ScanStatus.COMPLETED, 'SECRET RAW ERROR',
                  ({'id': 1, 'name': 'Public source', 'url': 'https://example.org',
                    'organisation': 'Org', 'api_key': 'SECRET KEY', 'framework': 'SECRET FRAMEWORK'},))
    items = [Evidence(i, 10, 1, 'COURSE', f'Course {i}', None, 'Org',
                      f'https://example.org/course/{i}', 'engineering learning outcomes ' * 40, now)
             for i in range(1, 12)]
    return run, items


def test_complete_multipart_allowlist_checksums_and_zip():
    run, items = fixture()
    files = build_handover(run, items, max_part_bytes=3500)
    manifest = json.loads(files['manifest.json'])
    parts = [json.loads(data) for name, data in files.items() if name.startswith('evidence_part_')]
    assert len(parts) > 1
    assert [e['id'] for p in parts for e in p['evidence']] == list(range(1, 12))
    assert all(p['part_count'] == len(parts) for p in parts)
    assert all(len(data) <= 3500 for name, data in files.items() if name.startswith('evidence_part_'))
    assert parts[0]['evidence'][0]['article_text'] == items[0].article_text
    assert sum(o['evidence_count'] for o in json.loads(files['organised_scan.json'])['organisations']) == 11
    assert b'SECRET' not in b''.join(files.values())
    assert manifest['prior_pruning_verified'] is False
    for entry in manifest['files']:
        assert hashlib.sha256(files[entry['name']]).hexdigest() == entry['sha256']
        assert len(files[entry['name']]) == entry['bytes']
    with ZipFile(BytesIO(zip_handover(files))) as archive:
        assert set(archive.namelist()) == set(files)


def test_rejects_missing_pruned_crossbatch_and_duplicate_records():
    run, items = fixture()
    for evidence, kwargs in [([], {}), (items, {'retention_eligible': False}),
                             ([replace(items[0], scan_run_id=11)], {}),
                             ([items[0], items[0]], {})]:
        with pytest.raises(ValueError):
            build_handover(run, evidence, **kwargs)


def test_does_not_truncate_oversized_record_or_export_credentials():
    run, items = fixture()
    with pytest.raises(ValueError, match='exceeds'):
        build_handover(run, items, max_part_bytes=1024)
    with pytest.raises(ValueError, match='credential'):
        build_handover(run, [replace(items[0], url='https://user:secret@example.org/file')])


def test_uses_batch_snapshot_not_live_source():
    run, items = fixture()
    files = build_handover(run, items)
    assert json.loads(files['evidence_part_001.json'])['evidence'][0]['source_name'] == 'Public source'


def test_transfer_has_only_evidence_file_with_complete_content():
    from src.services.public_handover import build_transfer_handover
    run, items = fixture()
    files = build_transfer_handover(run, items)
    assert len(files) == 1
    assert set(files) == {'public_evidence_batch_10.txt'}
    data = files['public_evidence_batch_10.txt']
    payload = json.loads(data)
    assert len(payload['evidence']) == len(items)
    assert payload['evidence'][0]['article_text'] == items[0].article_text
    assert {'sources', 'source_health', 'organised_scan', 'manifest'} <= payload.keys()
    assert 'files' not in payload['manifest']
    assert payload['manifest']['transfer_file_count'] == 1
    assert b'SECRET' not in data


def test_original_summary_verifies_count_and_rejects_missing_text():
    from src.services.public_handover import build_transfer_handover
    run, items = fixture()
    files = build_transfer_handover(run, items, scan_summary={'evidence_count': len(items)})
    manifest = json.loads(files['public_evidence_batch_10.txt'])['manifest']
    assert manifest['original_scan_evidence_count'] == len(items)
    assert manifest['prior_pruning_verified'] is True
    with pytest.raises(ValueError, match='original scan'):
        build_transfer_handover(run, items[:-1], scan_summary={'evidence_count': len(items)})
