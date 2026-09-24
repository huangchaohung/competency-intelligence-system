from src.services.source_catalogue_import import catalogue_diff, deduplicate_catalogue_rows, normalise_catalogue_url, parse_catalogue_text, prepare_catalogue_rows


def test_catalogue_url_normalisation_removes_spreadsheet_escaping_and_trailing_slash() -> None:
    assert normalise_catalogue_url(r"https\://Example.ORG/path/") == "https://example.org/path"


def test_health_matching_preserves_case_sensitive_paths():
    from scripts.apply_source_health_stage import normalise_catalogue_url as health_key
    assert health_key("https://EXAMPLE.org/Research/a") != health_key("https://example.org/research/a")
    assert health_key("https://EXAMPLE.org/Research/a/") == health_key("https://example.org/Research/a")


def test_catalogue_deduplication_preserves_distinct_urls() -> None:
    rows = [
        {"Organisation": "Org", "Configured Discovery URL": "https://example.org/a/"},
        {"Organisation": "Org", "Configured Discovery URL": r"https\://example.org/a"},
        {"Organisation": "Org", "Configured Discovery URL": "https://example.org/b"},
    ]
    result = deduplicate_catalogue_rows(rows)
    assert [row["Configured Discovery URL"] for row in result] == ["https://example.org/a", "https://example.org/b"]


def test_prepare_catalogue_rows_preserves_family_and_role_and_infers_type() -> None:
    rows = prepare_catalogue_rows([{
        "Source Family": "Government Agency",
        "Organisation": "Org",
        "Source Role": "PRIMARY",
        "Configured Discovery URL": r"https\://example.org/standards",
    }])
    assert rows[0]["Source Family"] == "Government Agency"
    assert rows[0]["Source Role"] == "PRIMARY"
    assert rows[0]["Inferred Source Type"] == "FRAMEWORK"
    assert rows[0]["Import Status"] == "Staged for review"


def test_catalogue_diff_reports_added_removed_and_updated_urls() -> None:
    active = [{"Configured Discovery URL": "https://example.org/a", "Source Role": "PRIMARY"}, {"Configured Discovery URL": "https://example.org/old"}]
    staged = [{"Configured Discovery URL": "https://example.org/a", "Source Role": "SUPPORTING"}, {"Configured Discovery URL": "https://example.org/new"}]
    diff = catalogue_diff(active, staged)
    assert [row["Configured Discovery URL"] for row in diff["added"]] == ["https://example.org/new"]
    assert [row["Configured Discovery URL"] for row in diff["removed"]] == ["https://example.org/old"]
    assert [row["Configured Discovery URL"] for row in diff["updated"]] == ["https://example.org/a"]


def test_catalogue_text_parser_accepts_tab_separated_source_list() -> None:
    rows = parse_catalogue_text("Source Family\tOrganisation\tConfigured Discovery URL\nGovernment Agency\tOrg\thttps://example.org/news\n")
    assert rows[0]["Organisation"] == "Org"
    assert rows[0]["Configured Discovery URL"] == "https://example.org/news"
