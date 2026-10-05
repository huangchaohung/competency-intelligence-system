from types import SimpleNamespace
from src.services.evidence_duplicates import public_description_key


def evidence(slug='example', text='Identical topic description', org='IEEE PES'):
    return SimpleNamespace(url='https://resourcecenter.ieee-pes.org/education/webinars/'+slug,
                           organisation=org,
                           article_text='Public resource description only; full resource not retrieved.\n\n'+text)


def test_same_webinar_slide_description_has_same_identity():
    assert public_description_key(evidence()) == public_description_key(evidence('example_sld'))


def test_tsinghua_environment_home_alias_only_when_content_matches():
    a = SimpleNamespace(url='https://www.tsinghua.edu.cn/enven/', organisation='Tsinghua', article_text='Environmental research and teaching')
    b = SimpleNamespace(**vars(a))
    b.url += 'index.htm'
    assert public_description_key(a) == public_description_key(b)
    for field, value in [('article_text', a.article_text+' New research'),
                         ('organisation', 'Other'), ('url', b.url+'?edition=2')]:
        changed = SimpleNamespace(**vars(b))
        setattr(changed, field, value)
        assert public_description_key(a) != public_description_key(changed)
    b.url = 'https://www.tsinghua.edu.cn/enven/research.htm'
    assert public_description_key(b) is None


def test_rics_reviewed_pdf_aliases_require_matching_content_and_provenance():
    root = 'https://www.rics.org/content/dam/ricsglobal/documents/join-rics/'
    a = SimpleNamespace(url=root+'RICS-Associate-Assessment-Real-Estate-Agency-Feb-2017.pdf',
                        organisation='RICS', article_text='Associate assessment Real Estate Agency')
    b = SimpleNamespace(url=root+'real-estate-agency-pathway-guide-associate-rics%20(1).pdf',
                        organisation='RICS', article_text=a.article_text)
    assert public_description_key(a) == public_description_key(b)
    for field, value in [('article_text', a.article_text+' Revised'),
                         ('organisation', 'Other'), ('url', b.url+'?version=2')]:
        changed = SimpleNamespace(**vars(b))
        setattr(changed, field, value)
        assert public_description_key(a) != public_description_key(changed)
    b.url = root+'building_control_pathway_guide_associate_rics.pdf'
    assert public_description_key(b) is None


def test_nea_overview_alias_requires_identical_content_and_keeps_children():
    root = 'https://www.nea.gov.sg/our-services/waste-management/3r-programmes-and-resources'
    a = SimpleNamespace(url=root, organisation='NEA', article_text='Waste minimisation overview')
    b = SimpleNamespace(url=root+'/waste-minimisation-and-recycling', organisation='NEA', article_text=a.article_text)
    assert public_description_key(a) == public_description_key(b)
    b.article_text += ' Updated guidance'
    assert public_description_key(a) != public_description_key(b)
    b.url += '/at-work'
    assert public_description_key(b) is None


def test_sutd_trailing_slash_alias_requires_identical_text_and_organisation():
    a = SimpleNamespace(url='https://www.sutd.edu.sg/esd/education/undergraduate/courses',
                        organisation='SUTD', article_text='Course one and course two')
    b = SimpleNamespace(**vars(a))
    b.url += '/'
    assert public_description_key(a) == public_description_key(b)
    b.article_text += ' Course three'
    assert public_description_key(a) != public_description_key(b)
    b.article_text = a.article_text
    b.organisation = 'Other'
    assert public_description_key(a) != public_description_key(b)


def test_different_webinars_and_content_remain_distinct():
    assert public_description_key(evidence()) != public_description_key(evidence('another'))
    assert public_description_key(evidence()) != public_description_key(evidence('example_sld','Additional learning outcomes'))
    assert public_description_key(evidence()) != public_description_key(evidence(org='Other organisation'))


def test_not_a_global_text_deduplicator():
    item = evidence()
    item.url = 'https://university.example/courses/course-1'
    assert public_description_key(item) is None
    item = evidence()
    item.article_text = 'Actual full resource, not a landing description'
    assert public_description_key(item) is None


def test_workflow_deduplication_is_only_within_current_scan():
    from unittest.mock import Mock
    from datetime import datetime
    from src.models.domain import Source, ScanStatus
    from src.workflow.scan_workflow import ScanWorkflow
    base = evidence().url
    source = Source(1, 'IEEE', base, 'IEEE PES')
    sources, scans, scanner, extractor = Mock(), Mock(), Mock(), Mock()
    sources.list_enabled.return_value = [source]
    scans.create_run.return_value = SimpleNamespace(id=1)
    scans.complete_run.return_value = SimpleNamespace(id=1, status=ScanStatus.COMPLETED,
        started_at=datetime.now(), completed_at=datetime.now(), error_summary=None)
    scans.prune_evidence_to_recent_runs.return_value = 0
    scanner.fetch_url.side_effect = lambda url, name: SimpleNamespace(url=url)
    extractor.extract.side_effect = lambda page, *args: evidence(page.url.rsplit('/', 1)[-1])
    workflow = ScanWorkflow(sources, scans, scanner, extractor)
    workflow._router = SimpleNamespace(discover=lambda s: [base, base+'_sld'])
    workflow.run()
    assert scans.add_evidence.call_count == 1
    workflow.run()
    assert scans.add_evidence.call_count == 2
