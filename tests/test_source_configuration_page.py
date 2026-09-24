"""Tests for source configuration page helper behaviour."""
from __future__ import annotations

from src.dashboard.source_configuration import _catalogue_preview_changes, _catalogue_shape_changed, _describe_changes
from src.models.domain import Source
import pandas as pd
import pytest
from src.core.exceptions import ConfigurationError
from src.dashboard.source_configuration import _sources_from_table


def test_catalogue_shape_changed_detects_removed_source() -> None:
    """A validated draft becomes stale when the live catalogue has a different URL list."""
    current = [Source(None, "Keep", "https://example.com/keep", "Example")]
    pending = [
        Source(None, "Keep", "https://example.com/keep", "Example"),
        Source(None, "Remove", "https://example.com/remove", "Example"),
    ]

    assert _catalogue_shape_changed(current, pending)


def test_describe_changes_does_not_crash_on_stale_lengths() -> None:
    """The change describer should not raise if a stale draft slips through."""
    current = [Source(None, "Keep", "https://example.com/keep", "Example")]
    pending = [
        Source(None, "Keep updated", "https://example.com/keep", "Example"),
        Source(None, "Remove", "https://example.com/remove", "Example"),
    ]

    changes = _describe_changes(current, pending)

    assert changes[0]["Change"] == "Changed Name"


def test_catalogue_preview_changes_ignore_database_ids() -> None:
    """A YAML backup should not appear changed just because it lacks SQLite IDs."""
    current = [Source(7, "Keep", "https://example.com/keep", "Example")]
    preview = [Source(None, "Keep", "https://example.com/keep", "Example")]

    assert _catalogue_preview_changes(current, preview) == []


def test_catalogue_preview_changes_summarise_add_remove_update() -> None:
    """Backup preview should show URL-level differences before any restore action."""
    current = [
        Source(7, "Keep", "https://example.com/keep", "Example"),
        Source(8, "Remove", "https://example.com/remove", "Example"),
    ]
    preview = [
        Source(None, "Keep updated", "https://example.com/keep", "Example"),
        Source(None, "Add", "https://example.com/add", "Example"),
    ]

    changes = _catalogue_preview_changes(current, preview)

    assert [change["Change"] for change in changes] == ["Would add", "Would remove", "Would update"]


def test_dynamic_editor_delete_first_edit_remaining_and_add():
    current = [Source(1, 'Remove', 'https://example.org/a', 'Org'),
               Source(2, 'Keep', 'https://example.org/b', 'Org', article_url_pattern='keep-pattern')]
    table = pd.DataFrame([
        {'_key': 'id:2', 'Name': 'Updated', 'Discovery URL': 'https://example.org/new', 'Organisation': 'Org'},
        {'Name': 'Added', 'Discovery URL': 'https://example.org/c', 'Organisation': 'Org'}])
    proposed = _sources_from_table(current, table)
    assert proposed[0].id == 2
    assert proposed[0].article_url_pattern == 'keep-pattern'
    assert proposed[1].id is None
    assert proposed[1].max_articles_per_scan == 25
    changes = _describe_changes(current, proposed)
    assert any(c['Change'] == 'Removed source' and c['Source'] == 'Remove' for c in changes)
    assert any(c['Change'] == 'Added source' for c in changes)


def test_editor_can_add_to_empty_and_remove_all():
    assert _sources_from_table([], pd.DataFrame([{'Name': 'New', 'Discovery URL': 'https://example.org', 'Organisation': 'Org'}]))[0].name == 'New'
    current = [Source(1, 'Old', 'https://example.org', 'Org')]
    assert _sources_from_table(current, pd.DataFrame()) == []
    assert _describe_changes(current, [])[0]['Change'] == 'Removed source'


@pytest.mark.parametrize('row', [
    {'Name': '', 'Discovery URL': 'https://example.org', 'Organisation': 'Org'},
    {'_key': 'id:999', 'Name': 'Unknown'},
    {'Name': 'New', 'Discovery URL': 'https://example.org', 'Organisation': 'Org', 'Max articles': 1.5},
])
def test_editor_invalid_rows_raise_friendly_error(row):
    with pytest.raises(ConfigurationError):
        _sources_from_table([], pd.DataFrame([row]))
