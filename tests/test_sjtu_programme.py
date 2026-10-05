import pytest
from src.extractor.sjtu_programme import programme_text
from src.core.exceptions import ExtractionError


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
