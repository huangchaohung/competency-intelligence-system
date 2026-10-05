import pytest
from src.extractor.sjtu_programme import programme_text
from src.core.exceptions import ExtractionError
from src.workflow.scan_workflow import ScanWorkflow
from src.extractor.sjtu_programme import CIVIL_URL
from src.extractor.article_extractor import ArticleExtractor
from src.scanner.web_page_scanner import DownloadedPage
from src.models.domain import Source
from src.extractor.sjtu_programme import CLUSTER_LANGUAGES
from src.extractor.sjtu_programme import SUMMER_URL
from src.extractor.sjtu_programme import EXCHANGE_URL
from src.extractor.sjtu_programme import INTERNSHIP_URL


def test_internship_retains_training_not_eligibility():
    html = '<nav>MENU</nav><h2>About Summer Program</h2><div class="mce-content-body">'
    html += 'Research training with academic mentors and project collaboration. ' * 15 + '</div>'
    html += '<h2>What will participants receive?</h2><div class="mce-content-body">Research experience</div>'
    html += '<h2>Eligibility Requirements</h2><div class="mce-content-body">GPA NOISE</div>'
    result = ArticleExtractor().extract(DownloadedPage(INTERNSHIP_URL+'/', html), Source(1, 'SJTU', INTERNSHIP_URL, 'SJTU'), 1)
    assert 'Research experience' in result.article_text
    assert 'GPA NOISE' not in result.article_text and 'MENU' not in result.article_text
    assert 'not a list of lab projects' in result.article_text
    assert 'Internship' in result.title
    with pytest.raises(ExtractionError):
        programme_text(html.replace('What will participants receive?', 'Other'), INTERNSHIP_URL)
    with pytest.raises(ExtractionError):
        programme_text(html + html, INTERNSHIP_URL)


def test_exchange_keeps_academic_section_and_restrictions_only():
    academic = '3. PROGRAMS &amp; COURSES Restricted Programs and Courses. Mechanical Engineering. '
    academic += 'Academic programme descriptions and research fields. ' * 20
    block = '<div class="slide-door">'+academic+'</div>'
    html = '<div class="page-item"><div class="mce-content-body">'+block
    html += '<div class="slide-door">4. PREPARATION BEFORE ARRIVAL VISA NOISE</div></div></div>'
    text = programme_text(html, EXCHANGE_URL)
    assert 'Mechanical Engineering' in text and 'Restricted Programs' in text
    assert 'VISA NOISE' not in text and 'Mixed disciplines' in text
    with pytest.raises(ExtractionError):
        programme_text('<main>'+academic+'</main>', EXCHANGE_URL)
    with pytest.raises(ExtractionError):
        programme_text(html + html, EXCHANGE_URL)


def test_visiting_application_exclusion_is_exact():
    url = 'https://global.sjtu.edu.cn/en/study-sjtu/prospective/non-degree-programs/282'
    assert ScanWorkflow._is_utility_url(url)
    assert not ScanWorkflow._is_utility_url(EXCHANGE_URL)
    assert not ScanWorkflow._is_utility_url(SUMMER_URL)
    assert not ScanWorkflow._is_utility_url(url.replace('global.sjtu.edu.cn', 'other.example'))


def test_summer_overview_keeps_examples_and_mixed_scope_not_menu():
    text = 'Global Summer School courses include Data Science and Surgical Robotics. Chinese Law. '
    text += 'Academic lectures and cultural activities for international students. ' * 15
    html = '<nav>Work@SJTU</nav><div class="page-item">'+text+'</div>'
    result = ArticleExtractor().extract(DownloadedPage(SUMMER_URL, html), Source(1, 'SJTU', SUMMER_URL, 'SJTU'), 1)
    assert 'Surgical Robotics' in result.article_text and 'Chinese Law' in result.article_text
    assert 'Mixed disciplines' in result.article_text and 'not a complete' in result.article_text
    assert 'Work@SJTU' not in result.article_text
    assert 'Summer School' in result.title and result.url == SUMMER_URL
    with pytest.raises(ExtractionError):
        programme_text('<main>'+text+'</main>', SUMMER_URL)
    with pytest.raises(ExtractionError):
        programme_text(html + '<div class="page-item">'+text+'</div>', SUMMER_URL)


@pytest.mark.parametrize('url,language', CLUSTER_LANGUAGES.items())
def test_cluster_keeps_programme_identity_and_planned_status(url, language):
    body = (f'Engineering Cluster Program in {language}. Mechanical Engineering. Robotics (Planned). '
            + 'Engineering learning and programme information. ' * 25)
    html = '<nav>MENU NOISE</nav><div class="page-item">'+body+'</div>'
    html += '<div class="page-item"><div class="title">Fees</div>FEE NOISE</div>'
    result = ArticleExtractor().extract(DownloadedPage(url, html), Source(1, 'GIFT', url, 'SJTU'), 1)
    assert language in result.title and result.url == url
    assert 'Robotics (Planned)' in result.article_text
    assert 'NOISE' not in result.article_text
    with pytest.raises(ExtractionError):
        programme_text('<main>'+body+'</main>', url)
    with pytest.raises(ExtractionError):
        programme_text(html + '<div class="page-item">'+body+'</div>', url)


def civil_html():
    return ('<nav>Work@SJTU MENU</nav><div class="page-item"><div class="title">Programme Introduction</div>'
            + 'Civil engineering and sustainable construction. ' * 22 + '</div>'
            '<div class="page-item"><div class="title">What You’ll Study</div>Digital Twin Technology and Smart Construction Robotics</div>'
            '<div class="page-item"><div class="title">Fees</div>FEE NOISE</div>')


def test_civil_programme_extracts_study_content_with_specific_title():
    source = Source(1, 'GIFT', 'https://example.org', 'SJTU')
    result = ArticleExtractor().extract(DownloadedPage(CIVIL_URL, civil_html()), source, 1)
    assert 'Civil Engineering' in result.title
    assert 'Digital Twin Technology' in result.article_text
    assert 'Work@SJTU' not in result.article_text and 'FEE NOISE' not in result.article_text
    assert result.url == CIVIL_URL


def test_civil_requires_study_section_and_reviewed_url():
    with pytest.raises(ExtractionError):
        programme_text(civil_html().replace('What You’ll Study', 'Admissions'), CIVIL_URL)
    with pytest.raises(ExtractionError):
        programme_text(civil_html(), 'https://example.org/778')


def test_sjtu_placeholder_and_index_are_not_evidence_bodies():
    for path in ('/en/study-sjtu/prospective/degree-programs/825',
                 '/en/news-events/meet-sjtu/research'):
        assert ScanWorkflow._is_utility_url('https://global.sjtu.edu.cn' + path)
        assert ScanWorkflow._is_utility_url('https://global.sjtu.edu.cn' + path + '/')
        assert not ScanWorkflow._is_utility_url('https://other.example' + path)
    assert not ScanWorkflow._is_utility_url('https://global.sjtu.edu.cn/en/news-events/meet-sjtu/research/1234')
    for programme in ('794', '778', '278', '279'):
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
