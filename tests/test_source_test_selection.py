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
