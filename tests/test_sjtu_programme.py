import pytest
from src.extractor.sjtu_programme import programme_text
from src.core.exceptions import ExtractionError
from src.workflow.scan_workflow import ScanWorkflow


def test_sjtu_placeholder_and_index_are_not_evidence_bodies():
    for path in ('/en/study-sjtu/prospective/degree-programs/825',
                 '/en/news-events/meet-sjtu/research'):
        assert ScanWorkflow._is_utility_url('https://global.sjtu.edu.cn' + path)
        assert ScanWorkflow._is_utility_url('https://global.sjtu.edu.cn' + path + '/')
        assert not ScanWorkflow._is_utility_url('https://other.example' + path)
    assert not ScanWorkflow._is_utility_url('https://global.sjtu.edu.cn/en/news-events/meet-sjtu/research/1234')
    for programme in ('794', '778', '278', '279', '387'):
        assert not ScanWorkflow._is_utility_url('https://global.sjtu.edu.cn/en/study-sjtu/prospective/degree-programs/' + programme)


def test_sjtu_keeps_study_sections_and_nested_health_not_admin():
    content = 'Sustainable energy engineering and health science learning outcomes. ' * 15
    html = '<nav>SITE MENU</nav><div class="page-item"><div class="title">Programs Introduction</div>'+content+'</div>'
    html += '<div class="page-item"><div class="title">Sustainable Energy (SE)</div>Energy systems<div class="title">Health Science and Technology</div>Biomedical engineering</div>'
    html += '<div class="page-item"><div class="title">Fees</div>FEE NOISE</div>'
    result = programme_text(html)
    assert 'Biomedical engineering' in result
    assert 'SITE MENU' not in result and 'FEE NOISE' not in result
    assert 'not a complete syllabus' in result


def test_sjtu_missing_sections_fail_closed():
    with pytest.raises(ExtractionError):
        programme_text('<main>'+'Sustainable energy and health. '*100+'</main>')
