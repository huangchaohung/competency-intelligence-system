import pytest
from src.extractor.icheme_course import course_text, matches
from src.core.exceptions import ExtractionError


def test_academic_sections_keep_outcomes_not_promotional_sections():
    html = '<main><div class="umb-body"><h2>Overview</h2><p>'+'Process safety engineering learning and risk assessment. '*20+'</p>'
    html += '<strong>Learning outcomes</strong><ul><li>Lead a LOPA study</li></ul><h2>Who will benefit</h2><p>Engineers</p>'
    html += '<h2>Course outline</h2><ul><li>Protection layers</li></ul><h2>What delegates say</h2><p>TESTIMONIAL</p><h2>Fees</h2><p>PRICE</p></div></main>'
    text = course_text(html)
    assert 'Lead a LOPA study' in text and 'Protection layers' in text
    assert 'TESTIMONIAL' not in text and 'PRICE' not in text
    with pytest.raises(ExtractionError):
        course_text(html.replace('Course outline', 'Other'))


def test_only_reviewed_course_families_match():
    base = 'https://www.icheme.org/training-events/training/courses-a-z/'
    assert matches(base+'fundamentals-of-process-safety/date/')
    assert matches(base+'layer-of-protection-analysis-lopa/')
    assert not matches(base+'unreviewed-course/')
    assert not matches(base.replace('www.icheme.org','other.example')+'fundamentals-of-process-safety/')


@pytest.mark.parametrize('slug', [
    'hazop-study-for-team-leaders-and-team-members',
    'practical-distillation-technology',
    'production-process-and-emergency-systems-on-oil-and-gas-installations',
    'human-factors-module-3',
])
def test_additional_reviewed_families_are_exactly_scoped(slug):
    base = 'https://www.icheme.org/training-events/training/courses-a-z/'
    assert matches(base + slug + '/scheduled-course/')
    assert not matches(base + slug + '-unreviewed/')
    assert not matches(base.replace('https:', 'http:') + slug + '/')
