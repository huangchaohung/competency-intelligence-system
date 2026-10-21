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


def test_nested_named_skills_preserve_context_without_parent_duplication():
    html = b'''<main><h1>Skills Framework</h1><ul><li>Skills and competencies: Emerging skills include:
    <ul><li>Computational Design - Use of programming for design automation and optimisation.</li>
    <li><p>Green Building Strategy Implementation - Formulation of environmental sustainability plans throughout the building lifecycle.</p></li></ul>
    </li><li>Training programmes: Find our training providers.</li></ul></main>'''
    title, _, blocks, _ = extract(html, 'text/html', 'https://example.org/framework')
    row = dict(Scan_ID='S1', Parent_organisation='Example', Organisation_as_listed='Example',
               Mode='SCAN', Source_type='FRAMEWORK', Max_chars_per_card=3000, Export_id='test')
    card = make_card(row, 'https://example.org/framework', title, blocks, 15000)
    assert 'Skills and competencies: Computational Design - Use of programming' in card['article_text']
    assert 'Skills and competencies: Green Building Strategy Implementation' in card['article_text']
    assert card['article_text'].count('Computational Design') == 1
    assert not any('Training programmes' in b and b.startswith('Skills and competencies:') for b in blocks)


def test_professional_requirements_and_module_names_survive():
    for label in ('Competencies', 'Required modules'):
        html = f'<main><h1>Engineering</h1><ul><li>{label}:<ul><li>Design safe systems.</li><li>Evaluate operational risks and validate solutions against specified criteria.</li></ul></li></ul></main>'.encode()
        _, _, blocks, _ = extract(html, 'text/html', 'https://example.org/resource')
        assert f'{label}: Design safe systems.' in blocks


def test_paragraph_wrapped_parent_label_as_on_live_bca_page():
    html = b'''<main><h1>Skills Framework</h1><ul><li><p><b>Skills and competencies:</b> Details on emerging skills:</p>
    <ul><li><p><b>Computational Design</b> - Use of programming and computational strategies for design automation.</p></li>
    <li><p><b>Smart Facilities Management</b> - Integration of digital technologies into facility operations.</p></li></ul></li>
    <li><p>Training programmes: Browse courses.</p></li></ul></main>'''
    title, _, blocks, _ = extract(html, 'text/html', 'https://example.org/framework')
    row = dict(Scan_ID='S1', Parent_organisation='Example', Organisation_as_listed='Example',
               Mode='SCAN', Source_type='FRAMEWORK', Max_chars_per_card=3000, Export_id='test')
    card = make_card(row, 'https://example.org/framework', title, blocks, 15000)
    assert 'Skills and competencies: Computational Design' in card['article_text']
    assert 'Skills and competencies: Smart Facilities Management' in card['article_text']
    assert card['article_text'].count('Computational Design') == 1
