from types import SimpleNamespace
from src.services.scan_diagnostics import source_diagnostics


def test_diagnostics_are_source_specific_and_never_copy_secrets():
    run = SimpleNamespace(sources_snapshot=[{'name':'ICE'},{'name':'ICE Attributes'},{'name':'Good'}],
        error_summary='ICE: https://example.org/?token=secret: TimeoutError timed out; ICE Attributes: ExtractionError: body unavailable C:/private/file')
    assert source_diagnostics(run) == {'ICE':['TIMEOUT'],'ICE Attributes':['CONTENT_BODY_MISSING']}


def test_diagnostics_empty_and_unknown():
    run = SimpleNamespace(sources_snapshot=[{'name':'A'}],error_summary=None)
    assert source_diagnostics(run) == {}
    run.error_summary = 'A: unexpected secret detail'
    assert source_diagnostics(run) == {'A':['OTHER_SCAN_ERROR']}
