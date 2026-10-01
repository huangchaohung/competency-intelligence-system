import pytest
from src.workflow.scan_workflow import ScanWorkflow
from src.extractor.article_extractor import ArticleExtractor
from src.scanner.web_page_scanner import DownloadedPage
from src.models.domain import Source, SourceType
from src.core.exceptions import ExtractionError


def test_asce_meeting_form_is_not_a_standard():
    path = '/publications-and-news/codes-and-standards/committee-meeting-information-form'
    assert ScanWorkflow._is_utility_url('https://www.asce.org'+path)
    assert not ScanWorkflow._is_utility_url('https://www.asce.org/publications-and-news/codes-and-standards/standards')
    assert not ScanWorkflow._is_utility_url('https://other.example'+path)


def test_mit_intro_only_is_rejected_but_short_course_lists_remain(monkeypatch):
    url = 'https://professional.mit.edu/course-catalog'
    source = Source(1, 'MIT', url, 'MIT', source_type=SourceType.CATALOGUE)
    extractor = ArticleExtractor()
    monkeypatch.setattr(extractor, '_extract_catalogue_text', lambda soup:
        'Explore our Course Catalog below to discover dynamic offerings taught by leading faculty.')
    with pytest.raises(ExtractionError, match='no course records'):
        extractor.extract(DownloadedPage(url, '<main>Catalogue</main>'), source, 1)
    courses = 'Advanced Manufacturing Processes\n\nApplied Data Science and Machine Learning\n\nDigital Engineering Systems'
    monkeypatch.setattr(extractor, '_extract_catalogue_text', lambda soup: courses)
    assert extractor.extract(DownloadedPage(url, '<main>Catalogue</main>'), source, 1).article_text == courses
