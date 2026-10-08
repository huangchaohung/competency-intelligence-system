"""Temporary enabled-state changes without replacing source details."""
from dataclasses import replace
from src.core.exceptions import ConfigurationError

PDF_TEST_URLS = {
    'https://www.icheme.org/knowledge-networks/knowledge-resources/safety-centre/framework/knowledge-and-competence',
    'https://www.imda.gov.sg/assets/f9e0ac04-898f-4de7-bc89-e6b34aa2e7d8.pdf',
}


def select_only(sources, urls):
    selected = set(urls)
    if not selected or not selected.issubset({s.url for s in sources}):
        raise ConfigurationError('Choose at least one source from your current catalogue.')
    return [replace(s, enabled=s.url in selected) for s in sources]


def restore_selection(sources, previous):
    # Keep later edits, additions and removals; restore only known enabled flags.
    return [replace(s, enabled=previous.get(s.url, s.enabled)) for s in sources]
