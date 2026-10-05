import pytest
from src.extractor.harvard_course import URL, course_text
from src.extractor.article_extractor import ArticleExtractor
from src.models.domain import Source
from src.scanner.web_page_scanner import DownloadedPage
from src.core.exceptions import ExtractionError
from src.extractor.harvard_course import matches


def test_harvard_learning_outcomes_are_preserved():
    html = '<div class="group-course-description"><div class="field--name-field-course-nutshell">'
    html += '<h2 class="field__label">What you will learn</h2><ul><li>Build neural networks with Python and explain backpropagation.</li></ul></div>'
    html += '<div class="body field--name-body">Study practical models for supervised learning and evaluate their predictions with appropriate validation techniques.</div></div>'
    html += '<aside>You may also like: unrelated course</aside>'
    text = course_text(html)
    assert 'backpropagation' in text and 'validation techniques' in text
    assert 'unrelated course' not in text
    assert matches('https://pll.harvard.edu/course/data-science-r-basics')
    for url in ('https://pll.harvard.edu/catalog', 'https://other.example/course/test', 'https://pll.harvard.edu/course/', 'https://pll.harvard.edu.evil.example/course/test'):
        assert not matches(url)


def test_short_reviewed_description_excludes_related_courses():
    description = 'Learn how to manage and apply artificial intelligence in business and evaluate how technologies support a business strategy.'
    html = '<title>AI Strategy</title><div class="group-course-description"><div class="body field--name-body"><h2 class="field__label">Course description</h2><p>'+description+'</p></div></div>'
    html += '<div class="body field--name-body">View All Courses</div>'
    html += '<aside><h2>You may also like</h2>Unrelated Course</aside>'
    result = ArticleExtractor().extract(DownloadedPage(URL, html), Source(1, 'Harvard', URL, 'Harvard'), 3)
    assert description in result.article_text
    assert 'Unrelated Course' not in result.article_text
    assert result.evidence_type == 'COURSE' and result.url == URL
    assert result.title == 'AI Strategy'


def test_harvard_missing_or_duplicate_body_fails_closed():
    with pytest.raises(ExtractionError):
        course_text('<aside>'+'Suggested courses only. '*100+'</aside>')
    with pytest.raises(ExtractionError):
        course_text('<div class="group-course-description"><div class="body field--name-body">Short</div></div>')
    with pytest.raises(ExtractionError):
        course_text('<div class="group-course-description">' + '<div class="body field--name-body">Body</div>' * 2 + '</div>')
