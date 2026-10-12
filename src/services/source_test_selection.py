"""Temporary enabled-state changes without replacing source details."""
from dataclasses import replace
from src.core.exceptions import ConfigurationError

ASTAR_TEST_URLS = {
    'https://www.a-star.edu.sg/simtech/kto/industrial-automation',
    'https://www.a-star.edu.sg/Research/medical-technologies',
    'https://www.a-star.edu.sg/simtech/research/sustainability-informatics-strategy-%28sis%29',
}

def select_only(sources, urls):
    selected = set(urls)
    if not selected or not selected.issubset({s.url for s in sources}):
        raise ConfigurationError('Choose at least one source from your current catalogue.')
    return [replace(s, enabled=s.url in selected) for s in sources]


def restore_selection(sources, previous):
    # Keep later edits, additions and removals; restore only known enabled flags.
    return [replace(s, enabled=previous.get(s.url, s.enabled)) for s in sources]
