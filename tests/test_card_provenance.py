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
