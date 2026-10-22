from src.dashboard.collector import display_health_rows


def test_health_sort_labels_and_snapshot_preservation():
    rows = [dict(Source='empty', Status='No evidence', **{'Evidence items': 0}),
            dict(Source='one', Status='Low evidence', **{'Evidence items': 1}),
            dict(Source='error', Status='Error', **{'Evidence items': 12}),
            dict(Source='ten', Status='Low evidence', **{'Evidence items': 10})]
    shown = display_health_rows(rows)
    assert [r['Source'] for r in shown] == ['ten', 'one', 'error', 'empty']
    assert [r['Status'] for r in shown] == ['Healthy', 'Healthy', 'Error', 'No evidence']
    assert shown[0]['Number of evidence cards'] == 10
    assert all('Evidence items' not in r for r in shown)
    assert rows[1]['Status'] == 'Low evidence'
    assert rows[1]['Evidence items'] == 1


def test_health_presentation_can_be_reapplied():
    rows = [{'Status': 'Healthy', 'Evidence items': 4}]
    assert display_health_rows(display_health_rows(rows)) == display_health_rows(rows)
