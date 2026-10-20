import csv
import io
import json
from dataclasses import replace
import pytest
from test_public_handover import fixture
from src.services.competency_export import build_competency_handover


def test_current_scan_cards_limits_provenance_and_no_secrets():
    run, items = fixture()
    files = build_competency_handover(run, items)
    assert set(files) == {'cards_part_001.txt', 'organisation_status.txt', 'url_log.txt'}
    cards = json.loads(files['cards_part_001.txt'])
    assert len(cards) == 4
    assert all(len(json.dumps(c, ensure_ascii=False, separators=(',', ':'))) <= 1000 for c in cards)
    assert all(c['retrieval_method'] == 'CRAWLER' and c['text_shortened'] for c in cards)
    assert b'SECRET' not in b''.join(files.values())
    logs = list(csv.DictReader(io.StringIO(files['url_log.txt'].decode('utf-8-sig'))))
    assert len(logs) == len(items)
    assert sum(int(r['cards_produced']) for r in logs) == len(cards)
    assert all(not r['http_status'] for r in logs)
    assert any('budget' in r['reason_if_rejected'] for r in logs)


def test_unqualified_records_keep_coverage_and_dont_invent_cards():
    run, items = fixture()
    files = build_competency_handover(run, [replace(items[0], title='News', url='https://example.org/news/a')])
    assert json.loads(files['cards_part_001.txt']) == []
    assert b'CRAWLER_UNAVAILABLE' in files['organisation_status.txt']


def test_rejects_foreign_scan_and_credentials():
    run, items = fixture()
    for bad in [replace(items[0], scan_run_id=99), replace(items[0], url='https://user:pass@example.org/course')]:
        with pytest.raises(ValueError):
            build_competency_handover(run, [bad])


def test_streamlit_real_export_buttons():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_string('''
from test_public_handover import fixture
from src.dashboard.collector import render_download
run, items = fixture()
render_download(run, items, None)
''').run()
    assert not app.exception
    assert not app.get('download_button')
    app.button[0].click().run()
    assert not app.exception
    labels = [x.proto.label for x in app.get('download_button')]
    assert labels[:3] == ['Download cards_part_001.txt', 'Download organisation_status.txt', 'Download url_log.txt']
    app.run()
    assert not app.exception
