from src.scanner.competency_pilot import PilotCollector, excluded_resource, qualification


def test_login_and_enquiry_excluded_not_public_standards():
    assert excluded_resource('https://example.org/members-only/framework', '')
    assert excluded_resource('https://example.org/idp/profile/SAML2/Redirect/SSO', '')
    assert excluded_resource('https://example.org/course/request-information/', '')
    assert not excluded_resource('https://example.org/standards/engineering', '')


def test_training_promotion_not_competency():
    assert not qualification('https://example.org/training', 'Customised Training', 'Training', [
        'Our engineering training is customised with partners to address their needs and learning outcomes.'
    ])[0]


def test_seed_attempt_precedes_higher_scoring_sitemap_candidates():
    collector = PilotCollector()
    row = dict(Scan_ID='S1', Parent_organisation='Example', Organisation_as_listed='Example',
               Mode='SCAN', Source_type='FRAMEWORK', URL='https://example.org/start',
               Allowed_domains='example.org', Max_chars_per_card=3000, Max_cards=1,
               Max_chars_per_organisation=15000, Browser_rendering='No', Page_types_to_find='', Notes='',
               Export_id='test')
    calls = []
    collector.allowed_by_robots = lambda *args: True
    def raw(r, url, purpose='content', *args):
        if purpose == 'sitemap':
            return url, b'<urlset><url><loc>https://example.org/framework/curriculum</loc></url></urlset>', 'application/xml', collector.log(r,url,purpose=purpose)
        calls.append(url)
        return None
    collector.raw = raw
    collector.run([row])
    assert calls[0] == row['URL']
