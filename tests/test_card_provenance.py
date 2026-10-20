from src.scanner.competency_pilot import make_card, serial, qualification


def test_complete_sentences_and_explicit_metadata():
    row = dict(Scan_ID='S1', Parent_organisation='Example', Organisation_as_listed='Example',
               Mode='SCAN', Source_type='FRAMEWORK', Source_family='PROFESSIONAL_BODY',
               Export_id='unique-run', Max_chars_per_card=3000)
    sentence = 'Engineering competencies include systems design, technical assurance and safety requirements.'
    card = make_card(row, 'https://example.org/framework', 'Engineering competency framework',
                     [sentence, 'Engineering competencies ' + 'long text ' * 500], 15000)
    assert card['article_text'] == sentence
    assert len(serial(card)) <= 3000
    assert card['publication_date'] is None
    assert card['original_text_characters'] > 3000
    assert card['export_id'] == 'unique-run'


def test_product_certification_is_not_personnel_competency():
    good, reason = qualification('https://example.org/certification', 'Aircraft type certification',
                                'Aircraft type certification', ['Engineering requirements for aircraft type certification.'])
    assert not good and 'Product/asset' in reason


def test_export_rejects_mixed_counts():
    from types import SimpleNamespace
    import pytest
    from src.services.competency_export import build_competency_handover
    run = SimpleNamespace(id=1, completed_at=True)
    native = dict(run_id=1, export_id='abc', cards=[
        dict(parent_organisation='Example', export_id='abc')],
        statuses=[dict(Parent_organisation='Example', cards_produced=0)], logs=[])
    with pytest.raises(ValueError, match='organisation status'):
        build_competency_handover(run, [], scan_summary={'competency_result': native})
    native['statuses'][0]['cards_produced'] = 1
    with pytest.raises(ValueError, match='URL log'):
        build_competency_handover(run, [], scan_summary={'competency_result': native})
    native['logs'] = [dict(cards_produced=1, parent_organisation='Example')]
    native['cards'][0]['export_id'] = 'other'
    with pytest.raises(ValueError, match='Mixed scan'):
        build_competency_handover(run, [], scan_summary={'competency_result': native})


def test_redirect_export_checks_resolved_url_without_losing_requested_url():
    from types import SimpleNamespace
    import pytest
    from src.services.competency_export import build_competency_handover
    original, resolved = 'https://example.org/start', 'https://example.org/course'
    native = dict(run_id=1, export_id='abc', cards=[
        dict(parent_organisation='Example', scan_id='S1', url=resolved, export_id='abc')],
        statuses=[dict(Parent_organisation='Example', cards_produced=1)],
        logs=[dict(parent_organisation='Example', Scan_ID='S1', url=original,
                   resolved_url=resolved, cards_produced=1)])
    run = SimpleNamespace(id=1, completed_at=True)
    files = build_competency_handover(run, [], scan_summary={'competency_result': native})
    assert original.encode() in files['url_log_abc.txt']
    assert resolved.encode() in files['url_log_abc.txt']
    native['logs'][0]['resolved_url'] = 'https://example.org/unrelated'
    with pytest.raises(ValueError, match='provenance'):
        build_competency_handover(run, [], scan_summary={'competency_result': native})
    native['logs'][0]['resolved_url'] = resolved
    native['logs'][0]['Scan_ID'] = 'S2'
    with pytest.raises(ValueError, match='provenance'):
        build_competency_handover(run, [], scan_summary={'competency_result': native})


def test_collector_records_final_browser_card_url():
    from src.scanner.competency_pilot import PilotCollector
    row = dict(Scan_ID='S1', Parent_organisation='Example', Organisation_as_listed='Example',
               Mode='SCAN', Source_type='FRAMEWORK', URL='https://example.org/start',
               Allowed_domains='example.org', Max_chars_per_card=3000, Max_cards=1,
               Max_chars_per_organisation=15000, Browser_rendering='Required', Page_types_to_find='', Notes='')
    collector = PilotCollector()
    html = b'<main><h1>Competency Framework</h1><p>Engineering requirements include technical skills and professional assessments for accredited engineers.</p></main>'
    collector.raw = lambda r, u: (u, html, 'text/html', collector.log(r, u, 200, attempted=True))
    collector.rendered = lambda r, u: ('https://example.org/final', html, 'text/html',
                                     collector.log(r, u, 200, 'browser', attempted=True))
    collector.run([row])
    log = next(item for item in collector.logs if item['cards_produced'])
    assert log['url'] == row['URL']
    assert log['resolved_url'] == collector.cards[0]['url'] == 'https://example.org/final'
