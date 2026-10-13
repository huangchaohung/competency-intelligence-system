from dataclasses import replace
import pytest
from src.models.domain import Source
from src.services.source_test_selection import select_only, restore_selection
from src.core.exceptions import ConfigurationError


def test_selection_and_restore_preserve_details_and_originals():
    sources = [Source(1, 'One', 'https://example.org/a', 'Org', enabled=True),
               Source(2, 'Two', 'https://example.org/b', 'Org', enabled=False)]
    before = {s.url: s.enabled for s in sources}
    selected = select_only(sources, [sources[1].url])
    assert [s.enabled for s in selected] == [False, True]
    assert [s.enabled for s in sources] == [True, False]
    selected[0] = replace(selected[0], name='Edited')
    restored = restore_selection(selected, before)
    assert restored[0].name == 'Edited'
    assert [s.enabled for s in restored] == [True, False]
    assert restore_selection(selected[1:], before) == [sources[1]]


@pytest.mark.parametrize('urls', [[], ['https://missing.example']])
def test_invalid_selection_is_rejected(urls):
    with pytest.raises(ConfigurationError):
        select_only([Source(1, 'One', 'https://example.org/a', 'Org')], urls)


def test_new_sources_keep_their_enabled_state_on_restore():
    new = Source(3, 'New', 'https://example.org/new', 'Org', enabled=True)
    assert restore_selection([new], {'https://example.org/removed': False}) == [new]


def test_failed_cloud_pdf_is_disabled_but_preserved_in_defaults():
    from pathlib import Path
    from src.services.configuration_service import ConfigurationService
    sources = ConfigurationService(Path(__file__).resolve().parents[1] / 'config/sources.yaml').load_sources()
    by_name = {s.name: s for s in sources}
    assert not by_name['IMDA GenAI Technical Skills and Competencies'].enabled
    assert by_name['IMDA GenAI Technical Skills and Competencies'].url.endswith('sfw-for-ict-skills-in-genai.pdf')
    assert by_name['IChemE — Knowledge And Competence'].enabled


def test_three_cloud_unavailable_astar_sources_are_preserved_disabled():
    from pathlib import Path
    from src.services.configuration_service import ConfigurationService
    sources = ConfigurationService(Path(__file__).resolve().parents[1] / 'config/sources.yaml').load_sources()
    by_name = {s.name: s for s in sources}
    for name in ['A*STAR — Sustainability', 'A*STAR SIMTech — Industrial Automation', 'A*STAR — Medical Technologies']:
        assert not by_name[name].enabled
        assert by_name[name].url.startswith('https://www.a-star.edu.sg/')
    assert by_name['A*STAR Research Features'].enabled


def test_reviewed_nus_sit_exclusions_preserve_other_sources():
    from pathlib import Path
    from src.services.configuration_service import ConfigurationService
    sources = ConfigurationService(Path(__file__).resolve().parents[1] / 'config/sources.yaml').load_sources()
    by_name = {s.name: s for s in sources}
    for name in ['NUS Civil & Environmental Engineering — Courses', 'SIT — Engineering Systems',
                 'SIT — Sit Civil Engineering', 'SIT — Sustainable Built Environment']:
        assert not by_name[name].enabled
        assert by_name[name].url.startswith('https://')
    assert by_name['NUS Biomedical Engineering — Undergraduate'].enabled


def test_reviewed_skillsfuture_pages_are_paused_without_changing_ipma():
    from pathlib import Path
    from src.services.configuration_service import ConfigurationService
    sources = ConfigurationService(Path(__file__).resolve().parents[1] / 'config/sources.yaml').load_sources()
    by_url = {s.url: s for s in sources}
    for url in ['https://www.skillsfuture.gov.sg/skills-framework',
                'https://www.skillsfuture.gov.sg/skills-framework/skills-frameworks-faq']:
        assert not by_url[url].enabled
    assert by_url['https://ipma.world/ipma-standards-development-programme/icb4'].enabled


def test_reviewed_nus_process_fm_gis_sources_are_paused():
    from pathlib import Path
    from src.services.configuration_service import ConfigurationService
    sources = ConfigurationService(Path(__file__).resolve().parents[1] / 'config/sources.yaml').load_sources()
    by_url = {s.url: s for s in sources}
    for url in [
        'https://cde.nus.edu.sg/chbe/undergraduate/beng-che/specialisation/specialisation-in-process-engineering',
        'https://cde.nus.edu.sg/dbe/executive-course-for-facilities-management-fm',
        'https://fass.nus.edu.sg/geog/graduate-certificate-in-applied-geographic-information-systems',
    ]:
        assert not by_url[url].enabled
    assert by_url['https://cde.nus.edu.sg/bme/undergraduate'].enabled


def test_reviewed_smu_failures_preserve_separate_programmes_source():
    from pathlib import Path
    from src.services.configuration_service import ConfigurationService
    sources = ConfigurationService(Path(__file__).resolve().parents[1] / 'config/sources.yaml').load_sources()
    by_url = {s.url: s for s in sources}
    assert not by_url['https://masters.smu.edu.sg/programme/master-of-sustainability'].enabled
    assert not by_url['https://academy.smu.edu.sg/courses/project-management-course'].enabled
    assert by_url['https://sustainability.smu.edu.sg/education/programmes'].enabled


def test_five_reviewed_sit_courses_are_preserved_disabled():
    from pathlib import Path
    from src.services.configuration_service import ConfigurationService
    sources = ConfigurationService(Path(__file__).resolve().parents[1] / 'config/sources.yaml').load_sources()
    courses = [s for s in sources if s.url.startswith('https://www.singaporetech.edu.sg/sitlearn/courses/')]
    assert len(courses) == 5
    assert all(not s.enabled for s in courses)


def test_ice_cloud_blocked_sources_are_preserved_disabled():
    from pathlib import Path
    from src.services.configuration_service import ConfigurationService
    sources = ConfigurationService(Path(__file__).resolve().parents[1] / 'config/sources.yaml').load_sources()
    by_url = {s.url: s for s in sources}
    assert not by_url['https://www.ice.org.uk/attributes'].enabled
    assert not by_url['https://www.ice.org.uk/join-ice/attributes-for-professionally-qualified-membership'].enabled
