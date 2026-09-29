import pytest
from src.workflow.scan_workflow import ScanWorkflow


@pytest.mark.parametrize('url', [
    'https://www.asce.org/publications-and-news/codes-and-standards/committee-application-form',
    'https://www.nea.gov.sg/programmes-grants/grants-and-awards/',
    'https://www.3e.tsinghua.edu.cn/en/category/research-recruit-ra-en?lang=en',
])
def test_reviewed_non_evidence_pages_are_skipped(url):
    assert ScanWorkflow._is_utility_url(url)


@pytest.mark.parametrize('url', [
    'https://aisingapore.org/ai-models-that-protect-your-privacy/',
    'https://learning.energyinst.org/course/index.php?categoryid=40',
    'https://www.nea.gov.sg/programmes-grants/grants-and-awards/research-project',
    'https://example.org/en/category/research-recruit-ra-en',
])
def test_reviewed_exclusions_do_not_spread_to_other_resources(url):
    assert not ScanWorkflow._is_utility_url(url)
