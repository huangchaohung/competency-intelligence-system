from src.extractor.response_diagnostics import html_diagnostics


def test_diagnostics_do_not_disclose_response_payload():
    result = html_diagnostics('<title>SECRET</title><script>SECRET_TOKEN</script><p>Access denied incident SECRET_ID</p>')
    assert 'access-notice hint=True' in result
    assert 'main present=False' in result
    assert 'scripts=1' in result
    assert 'SECRET' not in result


def test_script_shell_is_not_asserted_to_be_blocked():
    result = html_diagnostics('<main></main><script>loadContent()</script>')
    assert 'visible words=0' in result
    assert 'main present=True' in result
    assert 'access-notice hint=False' in result
