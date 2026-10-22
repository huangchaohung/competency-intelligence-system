from src.scanner.competency_pilot import make_card, administrative_excerpt


def test_learner_statements_outrank_registration_and_biographies():
    blocks = [
        'Mark has been a Certified Energy Manager instructor since 2001 and teaches technical courses.',
        'You must register and pay for the certification application and exam separately.',
        'Learn how systems are intended to operate throughout a building, such as HVAC, lighting, motors, boilers, and controls.',
        'Understand the economic aspects of energy efficiency measures and present opportunities in financial terms.',
        'These training programs prepare participants to take the Certified Energy Manager exam.']
    row = dict(Scan_ID='S1', Parent_organisation='AEE', Organisation_as_listed='AEE',
               Mode='SCAN', Source_type='CATALOGUE', Max_chars_per_card=1500, Export_id='test')
    card = make_card(row, 'https://example.org/course', 'Energy auditing course', blocks, 15000)
    assert card['article_text'].startswith('Learn how systems')
    assert 'Understand the economic aspects' in card['article_text']
    assert 'register and pay' not in card['article_text']
    assert 'instructor since' not in card['article_text']


def test_personnel_certification_requirements_are_not_administration():
    assert not administrative_excerpt('Applicants must demonstrate engineering competence and complete an accredited examination.')
    assert not administrative_excerpt('Engineers must evaluate heat transfer costs and energy efficiency.')
