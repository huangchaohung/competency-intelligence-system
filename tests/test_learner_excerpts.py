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


def test_technical_learning_precedes_generic_sales_and_omits_interface_noise():
    blocks = [
        'Learn how to reduce the sales cycles and avoid pitfalls which delay projects.',
        'Learn how to measure and verify energy efficiency and water demand management.',
        'Understand the economic analysis of energy efficiency projects and life cycle costing.',
        'Contains 10 Component(s) , Includes Credits Overview Objectives Instructors Course Information.',
        'Please verify accuracy of your shipping address during course registration.',
        'Registration closes 2 business days before the technical course starts.']
    row = dict(Scan_ID='S1', Parent_organisation='AEE', Organisation_as_listed='AEE',
               Mode='SCAN', Source_type='CATALOGUE', Max_chars_per_card=3000, Export_id='test')
    card = make_card(row, 'https://example.org/course', 'Energy course', blocks, 15000)
    assert card['article_text'].startswith('Learn how to measure and verify energy')
    assert 'economic analysis of energy' in card['article_text']
    assert 'Component(s)' not in card['article_text']
    assert 'shipping' not in card['article_text']
    assert 'Registration closes' not in card['article_text']


def test_engineering_shipping_and_components_are_not_blanket_excluded():
    assert not administrative_excerpt('Learn how to design shipping systems for safe marine transport.')
    assert not administrative_excerpt('Describe mechanical components and validate their engineering requirements.')


def test_embedded_fee_sentence_and_honorific_are_omitted():
    row = dict(Scan_ID='S1', Parent_organisation='AEE', Organisation_as_listed='AEE',
               Mode='SCAN', Source_type='CATALOGUE', Max_chars_per_card=3000, Export_id='test')
    block = ('Learn how to evaluate energy systems and apply engineering standards. '
             'A separate certification and application fee applies. Dr. '
             'Engineering assessment includes validating requirements against measured performance.')
    card = make_card(row, 'https://example.org/course', 'Energy course', [block], 15000)
    assert 'Learn how to evaluate energy systems' in card['article_text']
    assert 'fee applies' not in card['article_text']
    assert '\nDr.' not in card['article_text']
