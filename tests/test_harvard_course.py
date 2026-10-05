import pytest
from src.extractor.harvard_course import URL, course_text
from src.extractor.article_extractor import ArticleExtractor
from src.models.domain import Source
from src.scanner.web_page_scanner import DownloadedPage
from src.core.exceptions import ExtractionError


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
