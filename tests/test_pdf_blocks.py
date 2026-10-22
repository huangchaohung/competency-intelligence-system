from src.scanner.pdf_blocks import pdf_blocks
from src.scanner.competency_pilot import make_card


def test_pdf_fragments_removed_and_limitations_exported_without_pdf_extension():
    from src.scanner.pdf_blocks import PdfBlocks
    from src.scanner.competency_pilot import serial
    blocks = PdfBlocks([
        'Engineers must validate technical requirements against stakeholder needs and demonstrate compliance through documented test evidence.',
        'Systems engineering requirements are implemented through product realiza -',
        'Requirements are', '34', 'EE 1234 Power Systems'])
    row = dict(Scan_ID='S1', Parent_organisation='Example', Organisation_as_listed='Example',
               Mode='SCAN', Source_type='FRAMEWORK', Max_chars_per_card=3000, Export_id='test')
    card = make_card(row, 'https://example.org/download?id=42', 'Engineering framework', blocks, 15000)
    assert 'documented test evidence.' in card['article_text']
    assert 'realiza' not in card['article_text']
    assert 'Requirements are' not in card['article_text']
    assert 'EE 1234 Power Systems' in card['article_text']
    assert 'verify claims' in card['extraction_limitations']
    assert len(serial(card)) <= 3000


def test_pdf_guard_does_not_modify_html_outcomes():
    from src.scanner.pdf_blocks import usable_pdf_unit
    assert not usable_pdf_unit('implementation of engineering require-')
    row = dict(Scan_ID='S1', Parent_organisation='Example', Organisation_as_listed='Example',
               Mode='SCAN', Source_type='CATALOGUE', Max_chars_per_card=3000, Export_id='test')
    card = make_card(row, 'https://example.org/course', 'Engineering course', [
        'Learning outcomes: Design sensors.',
        'Learning outcomes: Evaluate technical engineering systems against operational safety requirements.'], 15000)
    assert 'Design sensors.' in card['article_text']
    assert 'extraction_limitations' not in card


def test_pdf_extraction_uses_recovered_blocks(monkeypatch):
    from types import SimpleNamespace
    from src.scanner.competency_pilot import extract
    monkeypatch.setattr('pypdf.PdfReader', lambda _: SimpleNamespace(
        metadata={'/Title': 'Engineering framework'}, pages=[SimpleNamespace(
            extract_text=lambda: 'Engineers must define measurable technical requirements\nexpressed as verifiable statements.')]))
    title, _, blocks, links = extract(b'%PDF-test', 'application/pdf', 'https://example.org/framework.pdf')
    assert title == 'Engineering framework'
    assert blocks == ['Engineers must define measurable technical requirements expressed as verifiable statements.']
    assert links == []


def test_wrapped_competency_statement_remains_whole():
    blocks = pdf_blocks(['Engineers must define measurable technical requirements\n'
                         'expressed as verifiable statements and validate the\n'
                         'requirements against stakeholder needs.'])
    assert blocks == ['Engineers must define measurable technical requirements expressed as verifiable statements and validate the requirements against stakeholder needs.']
    row = dict(Scan_ID='S1', Parent_organisation='Example', Organisation_as_listed='Example',
               Mode='SCAN', Source_type='FRAMEWORK', Max_chars_per_card=3000, Export_id='test')
    card = make_card(row, 'https://example.org/framework.pdf', 'Engineering framework', blocks, 15000)
    assert card['article_text'] == blocks[0]


def test_do_not_join_across_pages_blanks_tables_or_page_numbers():
    assert pdf_blocks(['Engineers evaluate the technical system\n\nusing tests.',
                       'Engineers evaluate the technical system\n12\nusing tests.',
                       'Engineers evaluate the technical system\nColumn A    Column B',
                       'Engineers evaluate the technical system', 'using tests.']) == [
        'Engineers evaluate the technical system', 'using tests.',
        'Engineers evaluate the technical system', 'using tests.',
        'Engineers evaluate the technical system', 'Column A Column B',
        'Engineers evaluate the technical system', 'using tests.']


def test_preserve_list_items_headings_and_complete_sentences():
    assert pdf_blocks(['Learning outcomes:\nDesign safe systems.\n• assess risk\n• validate requirements\n'
                       'Engineers shall assess operational risk.\nvalidate results separately.']) == [
        'Learning outcomes:', 'Design safe systems.', '• assess risk', '• validate requirements',
        'Engineers shall assess operational risk.', 'validate results separately.']
