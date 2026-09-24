from datetime import datetime

import pytest

from src.core.exceptions import ExtractionError
from src.extractor.article_extractor import ArticleExtractor
from src.models.domain import Source, SourceRole, SourceType
from src.scanner.web_page_scanner import DownloadedPage


def test_biodesign_keeps_curriculum_not_alumni_or_cookie_dialog():
    source = Source(1, 'Biodesign', 'https://sgbiodesign.sg/fellowships/',
                    'Singapore Biodesign', source_type=SourceType.CATALOGUE)
    html = '''<main><h1>Innovation Fellowship</h1>
    <p>Identify clinical needs, invent medical technologies and implement solutions through multidisciplinary engineering training.</p>
    <section id="meet_the_fellows"><p>Alumni directory names</p></section></main>
    <dialog id="moove_gdpr_cookie_modal"><p>Strictly Necessary Cookies</p></dialog>'''
    text = ArticleExtractor().extract(DownloadedPage(source.url, html), source, 1).article_text
    assert 'invent medical technologies' in text
    assert 'Alumni directory' not in text
    assert 'Strictly Necessary' not in text
    other = ArticleExtractor().extract(DownloadedPage('https://example.org/course', html), source, 1).article_text
    assert 'Alumni directory' in other


def test_course_metadata_and_expanded_description_are_preserved():
    source = Source(1, 'Course', 'https://example.org/course', 'Org', source_type=SourceType.CATALOGUE)
    html = '''<main><h3>As Taught In</h3><div class="course-info-content">Fall 2016</div>
    <div id="collapsed-description"><p>Learn mechanics ...</p></div>
    <div id="expanded-description"><p>Learn mechanics through experiments and engineering design.</p></div></main>'''
    text = ArticleExtractor().extract(DownloadedPage(source.url, html), source, 1).article_text
    assert 'Fall 2016' in text
    assert 'Learn mechanics ...' not in text
    assert text.count('Learn mechanics') == 1


@pytest.mark.parametrize('title,body', [
    ('Chat with a student', '<p>Chat with our students about living here and choosing a programme.</p>'),
    ('ASD courses', '<h2>Undergraduate programme</h2><h2>Resources</h2><p>Explore our resources</p><h3>Academic calendar</h3><p>Get more details about your school terms, vacation periods and more.</p><h3>SUTD Courses</h3><p>Browse courses offered throughout SUTD, and discover the best fit for your interests.</p>'),
])
def test_rejects_known_short_catalogue_utility_pages(title, body):
    source = Source(1, 'Catalogue', 'https://example.org/courses', 'Org', source_type=SourceType.CATALOGUE)
    with pytest.raises(ExtractionError, match='Navigation-only'):
        ArticleExtractor().extract(DownloadedPage(source.url, f'<title>{title}</title><main>{body}</main>'), source, 1)


def test_short_course_list_survives_navigation_filter():
    text = 'Resources\n\nAcademic calendar\n\nFMT101 Building Services five credit units\n\nFMT201 Building Technology five credit units'
    assert not ArticleExtractor._is_short_catalogue_utility('Facilities management', text)
    source = Source(1, 'Courses', 'https://example.org/courses', 'Org', source_type=SourceType.CATALOGUE)
    evidence = ArticleExtractor().extract(DownloadedPage(source.url, '<main><h1>Engineering courses</h1><ul><li>Building services and systems</li><li>Structural engineering design</li></ul></main>'), source, 1)
    assert 'Structural engineering design' in evidence.article_text


def test_catalogue_preserves_main_inside_server_form():
    source = Source(1, 'Training', 'https://example.org/training', 'Org', source_type=SourceType.CATALOGUE)
    page = DownloadedPage(source.url, '<form><input value="secret"><main><h1>Structural engineering courses</h1><p>Learn reinforced concrete design and structural fire engineering in practical training.</p></main><button>Submit</button></form>')
    evidence = ArticleExtractor().extract(page, source, 1)
    assert 'reinforced concrete' in evidence.article_text
    assert 'secret' not in evidence.article_text
    assert 'Submit' not in evidence.article_text


def test_catalogue_keeps_card_descriptions_in_order_without_duplicates():
    source = Source(1, 'Training', 'https://example.org/training', 'Org', source_type=SourceType.CATALOGUE)
    page = DownloadedPage(source.url, '''<main>
        <h2>Temporary works design</h2><div class="card__body">Understand basic principles of temporary works design.</div>
        <h2>Fire engineering</h2><div class="card__body"><p>Learn structural performance in fire and risk analysis.</p></div>
        </main>''')
    text = ArticleExtractor().extract(page, source, 1).article_text
    assert text.index('Temporary works design') < text.index('Understand basic') < text.index('Fire engineering')
    assert text.count('Learn structural performance') == 1


def test_catalogue_excludes_navigation_card_descriptions():
    source = Source(1, 'Training', 'https://example.org/training', 'Org', source_type=SourceType.CATALOGUE)
    page = DownloadedPage(source.url, '<main><nav><div class="card__body">Navigation advertisement</div></nav><h2>Engineering training</h2><p>Study structural performance in fire through practical engineering exercises.</p></main>')
    assert 'Navigation advertisement' not in ArticleExtractor().extract(page, source, 1).article_text


def test_catalogue_preserves_definition_list_syllabus_and_availability():
    source = Source(1, 'Course', 'https://example.org/course', 'Org', source_type=SourceType.CATALOGUE)
    page = DownloadedPage(source.url, '''<main>
        <nav><dl><dt>Menu</dt><dd>Unrelated navigation</dd></dl></nav>
        <h1>Systems engineering</h1><h4>Course dates</h4>
        <center>Future courses are expected, but yet to be scheduled.<br></center>
        <dl><dt><h3>Engineering processes</h3></dt>
        <dd>Software supply chain management and assurance.<p>Independent verification and validation.</p></dd>
        <dt>Platform security</dt><dd>Trusted execution environments and access control.</dd></dl>
        </main>''')
    text = ArticleExtractor().extract(page, source, 1).article_text
    assert 'yet to be scheduled' in text
    assert 'Software supply chain management and assurance.' in text
    assert text.count('Engineering processes') == 1
    assert text.count('Independent verification and validation.') == 1
    assert text.index('Engineering processes') < text.index('Software supply') < text.index('Platform security')
    assert 'Trusted execution environments' in text
    assert 'Unrelated navigation' not in text


def test_pdf_scanner_output_is_readable_as_catalogue(monkeypatch):
    from types import SimpleNamespace
    from src.scanner import web_page_scanner as module
    text = 'FMT101 Building Services five credit units. FMT201 Building Technology. Design < modelling & assessment.'
    monkeypatch.setattr(module, 'PdfReader', lambda stream: SimpleNamespace(pages=[SimpleNamespace(extract_text=lambda: text)]))
    page = module.WebPageScanner()._download_pdf(SimpleNamespace(
        iter_content=lambda size: [b'%PDF-1.7 mock'], close=lambda: None,
        url='https://example.org/curriculum'), 'Course & programme')
    source = Source(1, 'Curriculum', page.url, 'Org', source_type=SourceType.CATALOGUE)
    evidence = ArticleExtractor().extract(page, source, 1)
    assert text == evidence.article_text


def test_framework_sources_preserve_hierarchy_and_are_explicit() -> None:
    """Framework sources should keep visible hierarchy and be marked explicit."""
    source = Source(
        None,
        "Framework",
        "https://example.org/framework",
        "Example Org",
        "Singapore",
        True,
        "Uncategorised",
        25,
        "",
        True,
        3,
        False,
        "standards / guidance",
        SourceType.FRAMEWORK,
        SourceRole.PRIMARY_DISCOVERY,
        True,
    )
    page = DownloadedPage(
        "https://example.org/framework",
        """
        <html>
          <head><title>Example Framework</title></head>
          <body>
            <h1>Example Framework</h1>
            <h2>Functional Area</h2>
            <h3>Sub Functional Area</h3>
            <ul><li>Competency One</li><li>Competency Two</li></ul>
          </body>
        </html>
        """,
    )

    evidence = ArticleExtractor().extract(page, source, 7)

    assert evidence.evidence_type == "EXPLICIT_COMPETENCY"
    assert evidence.explicit_or_inferred == "EXPLICIT"
    assert "Functional Area" in evidence.article_text
    assert "Competency One" in evidence.article_text


def test_catalogue_sources_preserve_record_style_text() -> None:
    """Catalogue sources should preserve repeated record-like structure."""
    source = Source(
        None,
        "Catalogue",
        "https://example.org/catalogue",
        "Example Org",
        "Singapore",
        True,
        "Uncategorised",
        25,
        "",
        True,
        3,
        False,
        "catalogue / training",
        SourceType.CATALOGUE,
        SourceRole.PRIMARY_DISCOVERY,
        True,
    )
    page = DownloadedPage(
        "https://example.org/catalogue",
        """
        <html>
          <head><title>Example Catalogue</title></head>
          <body>
            <article>
              <h2>Course A</h2>
              <p>Learn digital twin engineering.</p>
              <a href="/course-a">Course A</a>
            </article>
            <article>
              <h2>Course B</h2>
              <p>Learn systems engineering foundations.</p>
              <a href="/course-b">Course B</a>
            </article>
          </body>
        </html>
        """,
    )

    evidence = ArticleExtractor().extract(page, source, 7)

    assert evidence.evidence_type == "PROFESSIONAL_RESOURCE"
    assert evidence.explicit_or_inferred == "INFERRED"
    assert "Course A" in evidence.article_text
    assert "Course B" in evidence.article_text


def test_research_sources_are_classified_as_research_capability() -> None:
    """Research-oriented article sources should be typed as research capability evidence."""
    source = Source(
        None,
        "Research",
        "https://example.org/research",
        "Example Org",
        "Singapore",
        True,
        "Uncategorised",
        25,
        "",
        True,
        3,
        False,
        "research / report",
        SourceType.ARTICLE,
        SourceRole.PRIMARY_DISCOVERY,
        True,
    )
    page = DownloadedPage(
        "https://example.org/research",
        """
            <html>
              <head><title>Example Research</title></head>
              <body>
                <article>
                  <h1>Research Capabilities</h1>
                  <p>This research programme studies digital twin systems and robotics.</p>
                  <p>It develops applied capability through projects, pilots, and technical publications.</p>
                  <p>The output includes research reports and industry-facing summaries.</p>
                  <p>The work also explores modelling methods, testbeds, deployment practice, validation workflows, stakeholder engagement, and operational readiness across engineering contexts.</p>
                  <p>These activities inform future research capability, technical roadmaps, and applied STE programme design for partner organisations and public institutions.</p>
                  <p>Researchers publish lessons learned, prototype results, comparative analyses, implementation notes, and practical guidance that support the translation of ideas into operational engineering capability.</p>
                  <p>The page therefore contains enough detailed explanatory content to stand in for a realistic research capability source without depending on external infrastructure or live website access.</p>
                </article>
              </body>
            </html>
            """,
    )

    evidence = ArticleExtractor().extract(page, source, 7)

    assert evidence.evidence_type == "RESEARCH_CAPABILITY"
    assert evidence.explicit_or_inferred == "INFERRED"


def test_framework_extraction_rejects_too_little_text() -> None:
    """Framework pages still need enough visible content to be useful."""
    source = Source(
        None,
        "Framework",
        "https://example.org/framework",
        "Example Org",
        "Singapore",
        True,
        "Uncategorised",
        25,
        "",
        True,
        3,
        False,
        "standards / guidance",
        SourceType.FRAMEWORK,
        SourceRole.PRIMARY_DISCOVERY,
        True,
    )
    page = DownloadedPage("https://example.org/framework", "<html><head><title>Framework</title></head><body><h1>Only one line</h1></body></html>")

    with pytest.raises(ExtractionError):
        ArticleExtractor().extract(page, source, 7)
