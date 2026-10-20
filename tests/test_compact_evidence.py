import json
import pytest
from src.services.compact_evidence import compact_payload, excerpts


def test_compact_parts_bound_unicode_and_preserve_all_ids_and_priority():
    rows = [{'id': i, 'url': f'https://example.org/{i}', 'organisation': '工程',
             'source_type': 'FRAMEWORK' if i % 2 else 'ARTICLE',
             'article_text': '\n\n'.join(f'Section {n} engineering competency knowledge. ' * 12 for n in range(50))}
            for i in range(30)]
    files = compact_payload({'evidence': rows}, max_characters=10000)
    parts = [json.loads(data) for data in files.values()]
    assert len(parts) > 1
    assert all(len(data.decode('utf-8')) <= 10000 for data in files.values())
    all_rows = [r for p in parts for r in p['evidence']]
    assert sorted(r['id'] for r in all_rows) == list(range(30))
    assert [r['priority'] for r in all_rows] == sorted(r['priority'] for r in all_rows)
    assert all(r['text_shortened'] for r in all_rows)
    assert all(p['part_count'] == len(parts) for p in parts)
    stats = parts[0]['export_summary']
    assert all(p['export_summary'] == stats for p in parts)
    assert stats['records_included'] == 30
    assert stats['records_shortened'] == 30
    assert stats['original_text_characters'] == sum(len(r['article_text']) for r in rows)
    assert stats['excerpt_text_characters'] == sum(len(r['article_text']) for r in all_rows)
    assert rows[0]['article_text'] != all_rows[0]['article_text']


def test_excerpts_preserve_short_text_and_label_long_omissions():
    assert excerpts('A useful course description.', 1000) == ('A useful course description.', False)
    text, shortened = excerpts(' '.join('word'+str(i) for i in range(5000)), 1000)
    assert len(text) <= 1000 and shortened and '[... omitted ...]' in text
    assert 'word0' in text and 'word4999' in text


def test_oversized_metadata_fails_without_silent_loss():
    with pytest.raises(ValueError, match='metadata'):
        compact_payload({'evidence': [{'id': 1, 'title': 'x'*15000, 'article_text': 'text'}]}, 10000)


def test_direct_session_export_matches_conversion_without_full_export(monkeypatch):
    from test_public_handover import fixture
    from src.services.public_handover import build_transfer_handover
    from src.services.compact_evidence import build_compact_handover
    run, items = fixture()
    expected = compact_payload(json.loads(next(iter(build_transfer_handover(run, items).values()))))
    def forbidden(*args, **kwargs):
        raise AssertionError('Must not construct full-text export')
    monkeypatch.setattr('src.services.public_handover.build_transfer_handover', forbidden)
    assert build_compact_handover(run, items) == expected


def test_direct_export_preserves_validation():
    from dataclasses import replace
    from test_public_handover import fixture
    from src.services.compact_evidence import build_compact_handover
    run, items = fixture()
    for bad in [[], [items[0], items[0]], [replace(items[0], scan_run_id=999)],
                [replace(items[0], url='https://user:secret@example.org/a')]]:
        with pytest.raises(ValueError):
            build_compact_handover(run, bad)
    with pytest.raises(ValueError, match='original scan'):
        build_compact_handover(run, items, scan_summary={'evidence_count': 999})
    with pytest.raises(ValueError, match='finished'):
        build_compact_handover(replace(run, completed_at=None), items)
