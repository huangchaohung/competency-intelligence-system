from src.scanner.competency_pilot import PilotCollector, canonical, excluded_resource


def test_safe_default_port_normalisation():
    assert canonical('https://example.org:443/course#section') == 'https://example.org/course'
    assert canonical('https://www.example.org/course') != canonical('https://example.org/course')
    assert canonical('http://example.org/course') != canonical('https://example.org/course')


def test_annual_report_is_rejected_before_network():
    collector = PilotCollector()
    assert collector.raw({'Scan_ID': 'S1'}, 'https://example.org/docs/annual-reports/report.pdf') is None
    assert 'before download' in collector.logs[-1]['reason_if_rejected']
    assert not collector.logs[-1]['attempted']
    assert excluded_resource('https://example.org/annual-report/2024', '')


def test_202_and_duplicate_resolved_response_not_reported_as_content():
    collector = PilotCollector()
    collector.allowed_by_robots = lambda *args: True
    class Response:
        status_code = 202
        is_redirect = False
        headers = {'Content-Type': 'text/html'}
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def raise_for_status(self): pass
        def iter_content(self, size): yield b''
    calls = []
    def get(url, **kwargs):
        calls.append(url)
        return Response()
    collector.session.get = get
    row = dict(Scan_ID='S1', Allowed_domains='example.org')
    assert collector.raw(row, 'https://example.org:443/course') is None
    assert 'HTTP 202' in collector.logs[-1]['reason_if_rejected']
    assert collector.raw(row, 'https://example.org/course') is None
    assert len(calls) == 1
    assert 'Duplicate resolved' in collector.logs[-1]['reason_if_rejected']
    collector.raw(dict(row, Scan_ID='S2'), 'https://example.org/course')
    assert len(calls) == 2  # no attribution/cache leakage between source rows
