from src.scanner.competency_pilot import extract, make_card, excluded_resource, PilotCollector


def test_outcomes_heading_context_beats_readings():
    html = b'''<main><h1>Chemical biology</h1>
    <h2>Prerequisites</h2><p>Engineering course requirements include technical chemistry knowledge and recommended textbooks.</p>
    <h2>Learning outcomes</h2><ul><li>Design molecular probes to measure cellular interactions and evaluate experimental results.</li></ul>
    <h2>Reading list</h2><p>Read the technical course textbook before class.</p></main>'''
    title, headings, blocks, links = extract(html, 'text/html', 'https://example.org/course')
    row = dict(Scan_ID='S1', Parent_organisation='Example', Organisation_as_listed='Example',
               Mode='SCAN', Source_type='CATALOGUE', Max_chars_per_card=3000, Export_id='test')
    card = make_card(row, 'https://example.org/course', title, blocks, 15000)
    assert card['article_text'].startswith('Learning outcomes: Design molecular probes')
    assert not any(b.startswith('Learning outcomes: Read') for b in blocks)


def test_consultations_filtered_before_fetching():
    row = dict(Parent_organisation='IET', Allowed_domains='theiet.org', Page_types_to_find='framework')
    links = [('https://www.theiet.org/impact/submissions-archive/2024/framework', 'Framework'),
             ('https://www.theiet.org/competency-framework', 'Competency framework')]
    assert PilotCollector().candidate_links(row, links) == [links[1][0]]


def test_known_admin_false_positives_but_keep_actual_syllabus():
    assert excluded_resource('https://example.org/pdf', 'DIGITAL COMPETENCE CENTRE APPLICATION FOR SUPPORT, 2026')
    assert excluded_resource('https://example.org/certificate', 'Certification of Products and Articles')
    assert excluded_resource('https://example.org/gls-disqualification-framework', 'Framework')
    assert not excluded_resource('https://example.org/syllabus.pdf', 'New Course Proposal Form for paper pilot')


def test_nested_outcomes_are_not_repeated_and_short_actions_survive():
    html = b'''<main><h1>Engineering course</h1><h2>Learning Outcomes</h2>
    <table><tr><td><ul><li>Design sensors.</li>
    <li>Evaluate technical engineering systems against operational safety requirements.</li></ul></td></tr></table>
    <h2>Prerequisites</h2><p>Engineering course knowledge includes physics and technical mathematics requirements.</p></main>'''
    title, _, blocks, _ = extract(html, 'text/html', 'https://example.org/course')
    assert sum('Design sensors.' in b for b in blocks) == 1
    assert any(b.startswith('Prerequisites:') for b in blocks)
    row = dict(Scan_ID='S1', Parent_organisation='Example', Organisation_as_listed='Example',
               Mode='SCAN', Source_type='CATALOGUE', Max_chars_per_card=3000, Export_id='test')
    card = make_card(row, 'https://example.org/course', title, blocks + blocks, 15000)
    assert card['article_text'].count('Design sensors.') == 1
    assert card['article_text'].startswith('Learning Outcomes:')


def test_project_calls_excluded_without_excluding_training_requirements():
    assert excluded_resource('https://example.org/document.pdf', 'DCC - Call for Projects 2026')
    assert excluded_resource('https://example.org/document.pdf', '1 Terms and Conditions for DCC Support')
    assert not excluded_resource('https://example.org/document.pdf', 'Engineering professional competency requirements')
